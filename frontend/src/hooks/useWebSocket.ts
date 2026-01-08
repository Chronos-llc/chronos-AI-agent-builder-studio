import { useState, useEffect, useRef } from 'react';

export const useWebSocket = (url: string | null) => {
    const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
    const [readyState, setReadyState] = useState<number>(WebSocket.CLOSED);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!url) {
            return;
        }

        const socket = new WebSocket(url);
        ws.current = socket;

        socket.onopen = () => {
            setReadyState(socket.readyState);
        };

        socket.onclose = () => {
            setReadyState(socket.readyState);
        };

        socket.onmessage = (event) => {
            setLastMessage(event);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            socket.close();
        };
    }, [url]);

    const sendMessage = (message: string) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(message);
        } else {
            console.warn('WebSocket is not connected. Message not sent.');
        }
    };

    return { sendMessage, lastMessage, readyState };
};

export default useWebSocket;