// src/lib/stores/WebSocketStore.ts
import { writable, derived, get } from 'svelte/store';
import { conversations, currentMessage, previousMessage } from "$lib/stores/ConversationStore";
import { notificationStore } from './NotificationStore';

export const isConnected = writable(false);

function createWebSocketStore(url: string) {
    let socket: WebSocket | null = null;
    let subscribers = 0;
    let messageBuffer: any[] = [];
    let reconnectDelay = 2000;
    let reconnectTimer: any = null;
    let responseTimeoutTimer: any = null;
    const responseTimeoutDuration = 10000;

    const { subscribe, set } = writable<WebSocket | null>(null, () => {
        subscribers++;
        if (subscribers === 1) connect();

        return () => {
            subscribers--;
            if (subscribers === 0) disconnect();
        };
    });

    function connect() {
        socket = new WebSocket(url);

        socket.onopen = () => {
            console.log("WebSocket Connected");
            isConnected.set(true);
            clearTimeout(reconnectTimer);
        };

        socket.onclose = (event) => {
            console.log("WebSocket Disconnected");
            isConnected.set(false);
            reconnect();
        };
        socket.onmessage = (event) => {
            clearTimeout(responseTimeoutTimer);
            responseTimeoutTimer = setTimeout(() => {
                notificationStore.set({
                    message: "Waiting for chat model..",
                    type: "warning",
                });
            }, responseTimeoutDuration);

            const newChunk = JSON.parse(event.data);
            
            if(newChunk.role === "error") {
                notificationStore.set({
                    message: newChunk.content[0].text,
                    type: "error"
                });
                messageIncoming.set("false");
                currentMessage.set(get(previousMessage));
                clearTimeout(responseTimeoutTimer);
                return;
            }
            
            if (newChunk.status === "complete") {
                clearTimeout(responseTimeoutTimer);
                messageIncoming.set("false");
                return;
            }

            isSelecting.subscribe((selecting) => {
                if (selecting) {
                    messageBuffer.push(newChunk);
                } else {
                    while (messageBuffer.length > 0) {
                        const message = messageBuffer.shift();
                        conversations.addMessage(message);
                    }
                    conversations.addMessage(newChunk);
                }
            })();
        };

        set(socket);
    }

    function disconnect() {
        if (socket) {
            socket.close();
            socket = null;
            set(null);
        }
    }

    function reconnect() {
        if (!socket || socket.readyState === WebSocket.CLOSED) {
            console.log(`Attempting to reconnect in ${reconnectDelay}ms...`);
            reconnectTimer = setTimeout(connect, reconnectDelay);
        }
    }

    function sendMessage(message: any) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
            
            // Flag message as incoming and reset timeout
            messageIncoming.set("true");
            clearTimeout(responseTimeoutTimer);
            
            responseTimeoutTimer = setTimeout(() => {
                notificationStore.set({
                    message: "Waiting for chat model..",
                    type: "warning",
                });                
            }, responseTimeoutDuration);

            if (message.role != 'command') {
                conversations.addMessage(message);
            }
        } else {
            console.error("WebSocket is not connected.");
        }
    }


    return {
        subscribe,
        sendMessage,
        isConnected
    };
}

export const webSocketStore = createWebSocketStore(import.meta.env.VITE_WS_URL);

export const messageIncoming = writable("false");

export const isSelecting = writable(false);
