import uuid
import toml
from sqlalchemy.orm import Session
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import models
import schemas


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

    chat_model = _get_chat_model(message["meta_data"]["llm"])

    try:
        ai_message = ""
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
                    "conversation_id": conversation.id,
                    "meta_data": streaming_metadata,
                }
                yield chunk_to_send

        # Add the complete message to the versions list in the final metadata
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
        print(f"Error: {e}")
        raise


def _get_chat_model(settings: dict):
    config = toml.load("../settings.toml")
    model = settings["model"]
    max_tokens = settings.get("max_tokens", None)

    # Create a dictionary to store the keyword arguments
    kwargs = {}

    # Add max_tokens to kwargs only if it's not None
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    llm = None

    match model:
        case "GPT-4":
            llm = ChatOpenAI(
                model="gpt-4", api_key=config["api_keys"]["OPENAI_API_KEY"], **kwargs
            )
        case "GPT-4-Turbo":
            llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                api_key=config["api_keys"]["OPENAI_API_KEY"],
                **kwargs,
            )
        case "GPT-4-Vision":
            llm = ChatOpenAI(
                model="gpt-4-vision-preview",
                api_key=config["api_keys"]["OPENAI_API_KEY"],
                **kwargs,
            )
        case "Claude Opus":
            llm = ChatAnthropic(
                model="claude-3-opus-20240229",
                api_key=config["api_keys"]["ANTHROPIC_API_KEY"],
                **kwargs,
            )
        case "Claude Haiku":
            llm = ChatAnthropic(
                model="claude-3-haiku-20240307",
                api_key=config["api_keys"]["ANTHROPIC_API_KEY"],
                **kwargs,
            )
        case "Claude Sonnet":
            llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                api_key=config["api_keys"]["ANTHROPIC_API_KEY"],
                **kwargs,
            )
        case "Gemini Pro":
            llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                api_key=config["api_keys"]["GOOGLE_API_KEY"],
                convert_system_message_to_human=True,
                **kwargs,
            )
        case _:
            print("No matching model found: ", settings["model"])

    return llm


def generate_context(
    conversation: schemas.ConversationOut,
    message_dict: dict,
    from_message_id: schemas.MessageOut = None,
):
    VISION_MODELS = ["GPT-4-Vision", "Claude Opus", "Claude Sonnet", "Claude Haiku"]

    def filter_content(content):
        if message_dict["meta_data"]["llm"]["model"] not in VISION_MODELS:
            return [item for item in content if item["type"] != "image_url"]
        return content

    if from_message_id:
        context = []
        for message in conversation.messages:
            if message.id == from_message_id:
                break
            context.append((message.role, filter_content(message.content)))
        return context
    else:
        context = [
            (message.role, filter_content(message.content))
            for message in conversation.messages
        ]
        context.append(("user", filter_content(message_dict["content"])))

        return context


def generate_title(conversation_id: int, db: Session):
    conversation = get_conversation(conversation_id, db)

    if conversation.title or len(conversation.messages) < 2:
        return

    system_message = "You will be given the first few messages of a conversation that has taken place between a large language model and a user. Your job is to analyze the content of the messages and return a short, descriptive title for the conversation. If the content in the messages is generic (for example, an exchange of greetings with no real substance), just return an empty string for the title.\n\nYour response must be a valid json object with a 'title' key and your chosen title for the value."
    user_message = "Here's the conversation to analyze: \n\n"

    for message in conversation.messages:
        for content_block in message.content:
            if "text" in content_block and content_block["text"]:
                user_message += f"{message.role}: {content_block['text']}\n\n"

    model = ChatOpenAI(model="gpt-4-turbo-preview")
    chain = model | JsonOutputParser()
    result = chain.invoke([("system", system_message), ("user", user_message)])

    if "title" in result and result["title"]:
        print(result["title"])
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
