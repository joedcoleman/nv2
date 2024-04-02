type MessageRole = 'user' | 'assistant' | 'system' | 'command';

type Message = {
    id: string;
    role: MessageRole;
    content: any[];
    status?: string;
    conversation_id: string;
    created_at?: string;
    meta_data: Record<string, any>;
  }

type Conversation = {
  id: string
  title?: string
  messages: Message[]
  created_at?: string
  updated_at?: string
  meta_data?: Record<string, any> | null;
}

type Settings = {
  models: []
}

let conversations: Conversation[] = []