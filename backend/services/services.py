import uuid
import toml
import tiktoken
from typing import Optional
from sqlalchemy.orm import Session
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import models
import schemas
from services.websocket_manager import websocket_manager

config = toml.load("../settings.toml")


async def process_message(
    db: Session,
    message: schemas.MessageIn,
):
    # Determine if we should regenerate from a past message
    message_to_regenerate = message["meta_data"].get("message_to_regenerate", None)

    # Set response metadata
    metadata = {"llm": message["meta_data"]["llm"], "versions": []}
    streaming_metadata = {"llm": message["meta_data"]["llm"], "versions": []}

    # Get conversation
    conversation = get_conversation(message["conversation_id"], db)

    if conversation is None:
        conversation = create_conversation(message["conversation_id"], db)

    # Generate context for request
    if message_to_regenerate:
        past_message = get_message(message_to_regenerate, db)
        context = generate_context(
            conversation, message_dict=message, from_message_id=past_message.id
        )
        ai_message_id = past_message.id

        # Add past versions to metadata
        metadata["versions"] = past_message.meta_data.get("versions", [])
    else:
        context = generate_context(conversation, message_dict=message)
        ai_message_id = str(uuid.uuid4())

    print("Getting chat model..")

    chat_model = _get_chat_model(message["meta_data"]["llm"])

    print("Using chat model: ", chat_model)

    try:
        ai_message = ""
        streaming_metadata = {}
        print("Streaming response!")
        async for chunk in chat_model.astream(context):
            if chunk.content:
                ai_message += chunk.content
                current_version = {
                    "role": "assistant",
                    "content": [{"type": "text", "text": ai_message}],
                    "meta_data": {k: v for k, v in metadata.items() if k != "versions"},
                }
                streaming_metadata = {
                    "llm": message["meta_data"]["llm"],
                    "versions": [current_version] + metadata["versions"],
                }
                chunk_to_send = {
                    "id": ai_message_id,
                    "role": "assistant",
                    "content": [{"type": "text", "text": chunk.content}],
                    "status": "incomplete",
                    "conversation_id": conversation.id,
                    "meta_data": streaming_metadata,
                }
                yield chunk_to_send

        completion_message = {
            "id": ai_message_id,
            "role": "assistant",
            "content": [{"type": "text", "text": ai_message}],
            "status": "complete",
            "conversation_id": conversation.id,
            "meta_data": streaming_metadata,
        }

        await websocket_manager.send_message(completion_message)

        metadata["versions"].insert(
            0,
            {
                "role": "assistant",
                "content": [{"type": "text", "text": ai_message}],
                "meta_data": {k: v for k, v in metadata.items() if k != "versions"},
            },
        )

        # Save messages
        if message_to_regenerate:
            update_message(
                ai_message_id,
                message=schemas.MessageIn(
                    id=ai_message_id,
                    role="assistant",
                    content=[{"type": "text", "text": ai_message}],
                    conversation_id=message["conversation_id"],
                    meta_data=metadata,
                ),
                db=db,
            )
        else:
            create_message(
                schemas.MessageIn(
                    id=message["id"],
                    role="user",
                    content=message["content"],
                    conversation_id=message["conversation_id"],
                    meta_data=message["meta_data"],
                ),
                db,
            )
            create_message(
                schemas.MessageIn(
                    id=ai_message_id,
                    role="assistant",
                    content=[{"type": "text", "text": ai_message}],
                    conversation_id=message["conversation_id"],
                    meta_data=metadata,
                ),
                db,
            )

        title = generate_title(message["conversation_id"], db)
        if title:
            update_conversation(conversation.id, {"title": title}, db)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        error_message = {
            "id": str(uuid.uuid4()),
            "role": "error",
            "content": [{"type": "text", "text": str(e)}],
            "status": "error",
            "conversation_id": message["conversation_id"],
            "meta_data": {},
        }
        await websocket_manager.send_message(error_message)
        raise


def _get_chat_model(settings: dict):
    model = settings["model"]
    temperature = settings.get("temperature", None)
    request_timeout = 10
    kwargs = {}

    if temperature is not None:
        kwargs["temperature"] = temperature / 100

    llm = None

    match model:
        case "GPT-4":
            llm = ChatOpenAI(
                model="gpt-4o",
                api_key=config["api_keys"]["OPENAI_API_KEY"],
                request_timeout=request_timeout,
                **kwargs,
            )
        case "Claude Opus":
            llm = ChatAnthropic(
                model="claude-3-opus-20240229",
                anthropic_api_key=config["api_keys"]["ANTHROPIC_API_KEY"],
                default_request_timeout=request_timeout,
                **kwargs,
            )
        case "Claude Haiku":
            llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                anthropic_api_key=config["api_keys"]["ANTHROPIC_API_KEY"],
                default_request_timeout=request_timeout,
                **kwargs,
            )
        case "Claude Sonnet":
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20240620",
                anthropic_api_key=config["api_keys"]["ANTHROPIC_API_KEY"],
                default_request_timeout=request_timeout,
                **kwargs,
            )
        case "Gemini Pro":
            llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=config["api_keys"]["GOOGLE_API_KEY"],
                convert_system_message_to_human=True,
                **kwargs,
            )
        case "Llama 3":
            llm = ChatOpenRouter(
                model="meta-llama/llama-3-70b-instruct:nitro",
                **kwargs,
            )
        case _:
            print("No matching model found: ", settings["model"])

    return llm


def generate_context(
    conversation: schemas.ConversationOut,
    message_dict: dict,
    from_message_id: str = None,
):
    """Return context for LLM call, ensuring total token count doesn't exceed `max_tokens` and user message is always included."""

    max_tokens = message_dict["meta_data"]["llm"].get("max_tokens", None)

    user_message = None
    # Find the message that precedes the from_message_id
    if from_message_id:
        for index, message in enumerate(conversation.messages):
            if message.id == from_message_id:
                if index > 0:
                    user_message = conversation.messages[index - 1].content
                break

    if not user_message:
        user_message = message_dict["content"]

    total_tokens = encode_and_count_tokens(user_message)

    context = []

    system_message = message_dict["meta_data"]["llm"].get("instructions", None)
    if system_message:
        system_tokens = encode_and_count_tokens(system_message)
        if max_tokens is None or system_tokens <= max_tokens:
            context.append(("system", system_message))
            total_tokens += system_tokens

    if from_message_id:
        start_index = (
            conversation.messages.index(
                next(m for m in conversation.messages if m.id == from_message_id)
            )
            - 1
        )
        for message in conversation.messages[start_index:]:
            tokens = encode_and_count_tokens(message.content)
            if max_tokens and total_tokens + tokens > max_tokens:
                break
            context.append((message.role, message.content))
            total_tokens += tokens
    else:
        for message in conversation.messages:
            tokens = encode_and_count_tokens(message.content)
            if max_tokens and total_tokens + tokens > max_tokens:
                break
            context.append((message.role, message.content))
            total_tokens += tokens

    context.append(("user", user_message))

    return context


def encode_and_count_tokens(content: list | str):
    tokenizer = tiktoken.encoding_for_model("gpt-4")

    if type(content) == str:
        return len(list(tokenizer.encode(content)))

    tokens = 0
    for item in content:
        if "text" in item:
            tokens += len(list(tokenizer.encode(item["text"])))
        elif "image_url" in item:
            tokens += 1000  # Sloppy approximation

    return tokens


def generate_title(conversation_id: int, db: Session):
    conversation = get_conversation(conversation_id, db)

    if conversation.title or len(conversation.messages) < 2:
        return

    system_message = "You will be given the first few messages of a conversation that has taken place between a large language model and a user. Your job is to analyze the content of the messages and return a short title for the conversation. The title should be *no more* than 6 words--keep it succinct! If the content in the messages is generic (for example, an exchange of greetings with no real substance), just return an empty string for the title.\n\nYour response must be a valid json object with a 'title' key and your chosen title for the value."
    user_message = "Here's the conversation to analyze: \n\n"

    for message in conversation.messages:
        for content_block in message.content:
            if "text" in content_block and content_block["text"]:
                user_message += f"{message.role}: {content_block['text']}\n\n"

    model = ChatOpenAI(
        model="gpt-4-turbo-preview", api_key=config["api_keys"]["OPENAI_API_KEY"]
    )
    chain = model | JsonOutputParser()
    result = chain.invoke([("system", system_message), ("user", user_message)])

    if "title" in result and result["title"]:
        return result["title"]


def create_message(message: schemas.MessageIn, db: Session):
    db_message = models.Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def update_message(message_id: int, message: schemas.MessageIn, db: Session):
    db_message = (
        db.query(models.Message).filter(models.Message.id == message_id).first()
    )

    if db_message:
        update_data = message.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_message, key, value)

        db.commit()
        db.refresh(db_message)
        return db_message
    else:
        return None


def create_conversation(conversation_id: str, db: Session):
    db_conversation = models.Conversation(id=conversation_id)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def update_conversation(conversation_id: str, update_data: dict, db: Session):
    db_conversation = (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id)
        .first()
    )
    if db_conversation:
        for key, value in update_data.items():
            setattr(db_conversation, key, value)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    else:
        return None


def get_conversations(db: Session):
    return db.query(models.Conversation).all()


def get_conversation(conversation_id: str, db: Session):
    return (
        db.query(models.Conversation)
        .filter(models.Conversation.id == conversation_id)
        .first()
    )


def get_message(message_id: str, db: Session):
    return db.query(models.Message).filter(models.Message.id == message_id).first()


class ChatOpenRouter(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str

    def __init__(
        self,
        model: str,
        openai_api_key: Optional[str] = None,
        openai_api_base: str = "https://openrouter.ai/api/v1",
        **kwargs,
    ):
        openai_api_key = config["api_keys"]["OPENROUTER_API_KEY"]
        super().__init__(
            openai_api_base=openai_api_base,
            openai_api_key=openai_api_key,
            model_name=model,
            **kwargs,
        )
