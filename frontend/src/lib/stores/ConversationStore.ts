import { writable } from 'svelte/store';

function createConversationsStore() {
    const { subscribe, set, update } = writable<Conversation[]>([]);

    return {
        subscribe,
        set,
        initializeOrUpdateConversation: (loadedConversation: Conversation) => {
            update(conversations => {
                const conversationIndex = conversations.findIndex(
                    conversation => conversation.id === loadedConversation.id
                );

                if (conversationIndex !== -1) {
                    // Conversation exists, update it
                    conversations[conversationIndex] = loadedConversation;
                } else {
                    // New conversation, add it
                    conversations = [...conversations, loadedConversation];
                }

                // Also update the current conversation
                currentConversation.set(loadedConversation);

                return conversations;
            });
        },
        addMessage: (message: Message) => {
            update(conversations => {
                const conversationIndex = conversations.findIndex(
                    conversation => conversation.id === message.conversation_id
                );
        
                if (conversationIndex !== -1) {
                    // Clone the conversation to avoid direct mutation
                    const conversation = { ...conversations[conversationIndex] };
        
                    const existingMessageIndex = conversation.messages.findIndex(m => m.id === message.id);
        
                    if (existingMessageIndex !== -1) {
                        // Message exists, update its content
                        const updatedMessage = {
                            ...conversation.messages[existingMessageIndex],
                            content: conversation.messages[existingMessageIndex].content.map((item, index) => {
                                if (item.type === 'text' && message.content[index]?.type === 'text') {
                                    return {
                                        ...item,
                                        text: item.text + message.content[index].text,
                                    };
                                }
                                return item;
                            }),
                            meta_data: message.meta_data,
                        };
                        conversation.messages[existingMessageIndex] = updatedMessage;
                    } else {
                        // New message, add to messages array
                        conversation.messages = [...conversation.messages, message];
                    }
        
                    // Update the conversation's updated_at timestamp
                    conversation.updated_at = new Date().toISOString();
        
                    // Replace the updated conversation in the array
                    const updatedConversations = [
                        ...conversations.slice(0, conversationIndex),
                        conversation,
                        ...conversations.slice(conversationIndex + 1),
                    ];
        
                    currentConversation.set(conversation);
        
                    // Update the conversationList store if the conversation doesn't exist
                    conversationList.update(list => {
                        const existingConversationIndex = list.findIndex(c => c.id === conversation.id);
                        if (existingConversationIndex === -1) {
                            return [...list, conversation];
                        }
                        return list;
                    });
        
                    return updatedConversations;
                } else {
                    const newConversation: Conversation = {
                        id: message.conversation_id,
                        messages: [message],
                        updated_at: new Date().toISOString(), // Add the updated_at timestamp
                    };
        
                    currentConversation.set(newConversation);
        
                    // Add the new conversation to the conversationList store
                    conversationList.update(list => [...list, newConversation]);
        
                    return [...conversations, newConversation];
                }
            });
        },
    };
}

export const conversations = createConversationsStore();

export const conversationList = writable<Conversation[]>([]);

export const currentConversation = writable<Conversation | null>(null);

export const currentMessage = writable("");