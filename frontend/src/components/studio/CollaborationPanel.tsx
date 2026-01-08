import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../contexts/AuthContext';

interface CollaborationPanelProps {
    agentId: string;
    onClose: () => void;
}

interface Collaborator {
    id: string;
    name: string;
    avatar: string;
    isActive: boolean;
    cursorPosition?: { x: number; y: number };
}

interface CollaborationMessage {
    type: 'cursor' | 'selection' | 'message' | 'presence';
    userId: string;
    data: any;
    timestamp: number;
}

export const CollaborationPanel: React.FC<CollaborationPanelProps> = ({ agentId, onClose }) => {
    const { user } = useAuth();
    const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
    const [messages, setMessages] = useState<CollaborationMessage[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [isConnected, setIsConnected] = useState(false);

    // Ref to expose updateCursorPosition to parent components
    const cursorUpdateRef = React.useRef<((x: number, y: number) => void) | null>(null);

    const { sendMessage, lastMessage, readyState } = useWebSocket(
        `ws://localhost:8000/ws/collaboration/${agentId}`
    );

    const updateCursorPosition = React.useCallback((x: number, y: number) => {
        if (user) {
            const message: CollaborationMessage = {
                type: 'cursor',
                userId: user.id.toString(),
                data: { position: { x, y } },
                timestamp: Date.now()
            };
            sendMessage(JSON.stringify(message));
        }
    }, [user, sendMessage]);

    // Initialize ref with updateCursorPosition
    React.useEffect(() => {
        cursorUpdateRef.current = updateCursorPosition;
    }, [updateCursorPosition]);

    useEffect(() => {
        setIsConnected(readyState === WebSocket.OPEN);
    }, [readyState]);

    useEffect(() => {
        if (lastMessage) {
            try {
                const message = JSON.parse(lastMessage.data) as CollaborationMessage;
                handleIncomingMessage(message);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        }
    }, [lastMessage]);

    const handleIncomingMessage = (message: CollaborationMessage) => {
        setMessages(prev => [...prev, message]);

        switch (message.type) {
            case 'presence':
                setCollaborators(prev => {
                    const existingIndex = prev.findIndex(c => c.id === message.userId);
                    if (existingIndex >= 0) {
                        const updated = [...prev];
                        updated[existingIndex] = {
                            ...updated[existingIndex],
                            isActive: message.data.isActive,
                            cursorPosition: message.data.cursorPosition
                        };
                        return updated;
                    } else {
                        return [...prev, {
                            id: message.userId,
                            name: message.data.name,
                            avatar: message.data.avatar,
                            isActive: message.data.isActive,
                            cursorPosition: message.data.cursorPosition
                        }];
                    }
                });
                break;

            case 'cursor':
                setCollaborators(prev => prev.map(c =>
                    c.id === message.userId
                        ? { ...c, cursorPosition: message.data.position, isActive: true }
                        : c
                ));
                break;
        }
    };

    const sendChatMessage = () => {
        if (newMessage.trim() && user) {
            const message: CollaborationMessage = {
                type: 'message',
                userId: user.id.toString(),
                data: { text: newMessage },
                timestamp: Date.now()
            };
            sendMessage(JSON.stringify(message));
            setNewMessage('');
        }
    };

    return (
        <div className="collaboration-panel bg-gray-900 text-white p-4 rounded-lg shadow-lg w-80">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Collaboration</h3>
                <button
                    onClick={onClose}
                    aria-label="Close collaboration panel"
                    className="text-gray-400 hover:text-white transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <div className="status-indicator mb-4">
                <div className={`flex items-center ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                    <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                    <span className="text-sm">{isConnected ? 'Connected' : 'Disconnected'}</span>
                </div>
            </div>

            <div className="collaborators-list mb-4">
                <h4 className="text-sm font-medium mb-2">Active Collaborators</h4>
                <div className="space-y-2">
                    {collaborators.map(collaborator => (
                        <div key={collaborator.id} className="flex items-center p-2 rounded hover:bg-gray-800 transition-colors">
                            <div className="relative">
                                <img
                                    src={collaborator.avatar || '/default-avatar.png'}
                                    alt={collaborator.name}
                                    className="w-8 h-8 rounded-full mr-2"
                                />
                                {collaborator.isActive && (
                                    <div className="absolute bottom-0 right-0 w-2 h-2 bg-green-400 rounded-full border border-gray-900"></div>
                                )}
                            </div>
                            <span className="text-sm">{collaborator.name}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="chat-section">
                <div className="messages h-40 overflow-y-auto mb-2 border border-gray-700 rounded p-2">
                    {messages
                        .filter(m => m.type === 'message')
                        .map((message, index) => (
                            <div key={index} className="message mb-2 p-2 rounded bg-gray-800">
                                <div className="text-xs text-gray-400">
                                    {collaborators.find(c => c.id === message.userId)?.name || 'Unknown'}
                                </div>
                                <div className="text-sm">{message.data.text}</div>
                            </div>
                        ))}
                </div>

                <div className="message-input flex">
                    <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                        placeholder="Type a message..."
                        className="flex-1 bg-gray-800 border border-gray-700 rounded-l px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
                    />
                    <button
                        onClick={sendChatMessage}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-r transition-colors"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CollaborationPanel;