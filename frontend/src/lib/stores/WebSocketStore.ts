// src/lib/stores/WebSocketStore.ts
import { writable, derived } from 'svelte/store';
import { conversations } from "$lib/stores/ConversationStore";

export const isConnected = writable(false);

function createWebSocketStore(url: string) {
    let socket: WebSocket | null = null;
    let subscribers = 0;
    let messageBuffer: any[] = [];
    let reconnectDelay = 1000; // Delay between reconnection attempts (in milliseconds)
    let reconnectTimer: any = null;

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
            clearTimeout(reconnectTimer); // Clear the reconnect timer on successful connection
        };

        socket.onclose = (event) => {
            console.log("WebSocket Disconnected");
            isConnected.set(false);
            if (!event.wasClean) {
                reconnect(); // Attempt to reconnect if the connection was closed unexpectedly
            }
        };
        socket.onmessage = (event) => {
            const newChunk = JSON.parse(event.data);
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
            reconnectDelay *= 2; // Double the reconnect delay for each attempt (exponential backoff)
        }
    }

    function sendMessage(message: any) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
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

export const isSelecting = writable(false);
