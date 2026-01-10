/// <reference types="vite/client" />
import React, { useState, useEffect, useRef } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Send, BookOpen, Play, Pause, Square, X, AlertCircle, ThumbsUp, ThumbsDown, Flag, Edit, AlertTriangle } from 'lucide-react'

interface ChatMessage {
    id: string
    role: 'user' | 'agent' | 'system'
    content: string
    timestamp: string
    status?: 'sent' | 'delivered' | 'read'
    isError?: boolean
    reactions?: Array<{
        type: 'like' | 'dislike' | 'flag'
        count: number
    }>
}

interface TrainingSession {
    id: string
    agentId: string
    startedAt: string
    status: 'active' | 'paused' | 'completed'
    trainingMode: 'standard' | 'advanced'
}

interface TrainingInteraction {
    id: string
    sessionId: string
    userInput: string
    agentResponse: string
    timestamp: string
    feedback?: string
}

interface ChatTesterProps {
    agentId: string
    onClose: () => void
}

export const ChatTester: React.FC<ChatTesterProps> = ({ agentId, onClose }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [inputValue, setInputValue] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [trainingSession, setTrainingSession] = useState<TrainingSession | null>(null)
    const [isTrainingMode, setIsTrainingMode] = useState(false)
    const [trainingInteractions, setTrainingInteractions] = useState<TrainingInteraction[]>([])
    const [currentFeedback, setCurrentFeedback] = useState('')
    const [feedbackTarget, setFeedbackTarget] = useState<string | null>(null)
    const [isPaused, setIsPaused] = useState(false)

    const messagesEndRef = useRef<HTMLDivElement>(null)
    
    const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000'
    const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws')
    const token = localStorage.getItem('access_token')
    
    const wsUrl = trainingSession && token 
        ? `${WS_BASE_URL}/api/v1/agents/${agentId}/training/real-time?session_id=${trainingSession.id}&token=${token}`
        : null

    const { sendMessage, lastMessage } = useWebSocket(wsUrl)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    useEffect(() => {
        if (lastMessage) {
            try {
                const parsedMessage = JSON.parse(lastMessage.data)
                if (parsedMessage.type === 'training_update') {
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'system',
                        content: parsedMessage.message,
                        timestamp: new Date().toISOString(),
                        status: 'delivered'
                    }])
                } else if (parsedMessage.type === 'agent_response') {
                    // Handle agent responses from WebSocket
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        role: 'agent',
                        content: parsedMessage.content,
                        timestamp: new Date().toISOString(),
                        status: 'delivered'
                    }])
                    setIsLoading(false)
                } else if (parsedMessage.type === 'interaction_recorded') {
                    // Update training interactions when recorded by backend
                    setTrainingInteractions(prev => [...prev, parsedMessage.interaction])
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error)
            }
        }
    }, [lastMessage])

    const startTrainingSession = async () => {
        try {
            setIsLoading(true)
            const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/training/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    agent_id: agentId,
                    training_mode: 'standard'
                })
            })

            if (!response.ok) {
                throw new Error('Failed to start training session')
            }

            const session = await response.json()
            setTrainingSession(session)
            setIsTrainingMode(true)
            setMessages([
                {
                    id: Date.now().toString(),
                    content: 'Training session started. Begin interacting with the agent.',
                    role: 'agent',
                    timestamp: new Date().toISOString()
                }
            ])
        } catch (error) {
            console.error('Error starting training session:', error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Error: ${(error as any)?.message || 'Unknown error'}`,
                role: 'agent',
                timestamp: new Date().toISOString(),
                isError: true
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const endTrainingSession = async () => {
        try {
            setIsLoading(true)
            if (!trainingSession) return

            const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/training/sessions/${trainingSession.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    status: 'completed'
                })
            })

            if (!response.ok) {
                throw new Error('Failed to end training session')
            }

            setIsTrainingMode(false)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: 'Training session completed. Thank you for your feedback!',
                role: 'agent',
                timestamp: new Date().toISOString()
            }])
        } catch (error) {
            console.error('Error ending training session:', error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Error: ${(error as any)?.message || 'Unknown error'}`,
                role: 'agent',
                timestamp: new Date().toISOString(),
                isError: true
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const togglePauseTraining = async () => {
        try {
            if (!trainingSession) return

            const newStatus = isPaused ? 'active' : 'paused'
            const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/training/sessions/${trainingSession.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    status: newStatus
                })
            })

            if (!response.ok) {
                throw new Error(`Failed to ${isPaused ? 'resume' : 'pause'} training session`)
            }

            setIsPaused(!isPaused)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Training session ${isPaused ? 'resumed' : 'paused'}.`,
                role: 'agent',
                timestamp: new Date().toISOString()
            }])
        } catch (error) {
            console.error(`Error ${isPaused ? 'resuming' : 'pausing'} training session:`, error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Error: ${(error as any)?.message || 'Unknown error'}`,
                role: 'agent',
                timestamp: new Date().toISOString(),
                isError: true
            }])
        }
    }

    const handleSendMessage = async () => {
        if (!inputValue.trim() || isLoading) return

        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            timestamp: new Date().toISOString(),
            status: 'sent'
        }

        setMessages(prev => [...prev, userMessage])
        const currentInput = inputValue
        setInputValue('')
        setIsLoading(true)

        try {
            // If in training mode, use WebSocket for real-time communication
            if (isTrainingMode && trainingSession && wsUrl) {
                // Send message via WebSocket
                const messageData = JSON.stringify({
                    session_id: trainingSession.id,
                    message: currentInput,
                    type: 'user_message'
                })
                sendMessage(messageData)

                // The agent response will come through the WebSocket onmessage handler
                // which is already set up in the useWebSocket hook
            } else {
                // Standard chat mode (mocked for now)
                setTimeout(() => {
                    const agentResponse = `Agent response to: "${currentInput}"`
                    const agentMessage: ChatMessage = {
                        id: Date.now().toString(),
                        role: 'agent',
                        content: agentResponse,
                        timestamp: new Date().toISOString(),
                        status: 'delivered'
                    }
                    setMessages(prev => [...prev, agentMessage])
                    setIsLoading(false)
                }, 1000)
                return // Exit early for non-training mode
            }
        } catch (error) {
            console.error('Error sending message:', error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Error: ${(error as any)?.message || 'Unknown error'}`,
                role: 'agent',
                timestamp: new Date().toISOString(),
                isError: true
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleProvideFeedback = (interactionId: string) => {
        setFeedbackTarget(interactionId)
        setCurrentFeedback('')
    }

    const submitFeedback = async () => {
        if (!currentFeedback.trim() || !feedbackTarget) return

        try {
            setIsLoading(true)

            // Find the interaction that this feedback is for
            const interaction = trainingInteractions.find(i => i.id === feedbackTarget)

            if (!interaction) {
                throw new Error('Interaction not found')
            }

            const response = await fetch(`${API_BASE_URL}/api/v1/agents/${agentId}/training/corrections`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    session_id: trainingSession?.id,
                    interaction_id: feedbackTarget,
                    content: currentFeedback,
                    correction_type: 'response' // Changed from 'user_feedback' to match enum
                })
            })

            if (!response.ok) {
                throw new Error('Failed to submit feedback')
            }

            // Add feedback message to chat
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Feedback submitted: ${currentFeedback}`,
                role: 'system',
                timestamp: new Date().toISOString(),
                status: 'delivered'
            }])

            // Clear feedback state
            setFeedbackTarget(null)
            setCurrentFeedback('')

        } catch (error) {
            console.error('Error submitting feedback:', error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: `Error submitting feedback: ${(error as any)?.message || 'Unknown error'}`,
                role: 'system',
                timestamp: new Date().toISOString(),
                status: 'delivered',
                isError: true
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            if (feedbackTarget) {
                submitFeedback()
            } else {
                handleSendMessage()
            }
        }
    }

    return (
        <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
            <div className="border-b p-4 bg-gray-50">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-bold text-gray-800">Chat Tester</h2>
                    <div className="flex gap-2">
                        {!isTrainingMode ? (
                            <button
                                onClick={startTrainingSession}
                                disabled={isLoading || isTrainingMode}
                                className="flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm font-medium transition-colors"
                            >
                                <BookOpen className="mr-2 h-4 w-4" />
                                Start Training
                            </button>
                        ) : (
                            <>
                                <button
                                    onClick={togglePauseTraining}
                                    disabled={isLoading}
                                    className={`flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${isPaused ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"}`}
                                >
                                    {isPaused ? <Play className="mr-2 h-4 w-4" /> : <Pause className="mr-2 h-4 w-4" />}
                                    {isPaused ? 'Resume' : 'Pause'}
                                </button>
                                <button
                                    onClick={endTrainingSession}
                                    disabled={isLoading}
                                    className="flex items-center px-3 py-1.5 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 text-sm font-medium transition-colors"
                                >
                                    <Square className="mr-2 h-4 w-4" />
                                    End Training
                                </button>
                            </>
                        )}
                        <button 
                            onClick={onClose}
                            className="flex items-center px-3 py-1.5 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 text-sm font-medium transition-colors"
                        >
                            <X className="mr-2 h-4 w-4" />
                            Close
                        </button>
                    </div>
                </div>

                {isTrainingMode && trainingSession && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                        <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${isPaused ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}`}>
                                    {trainingSession.status.toUpperCase()}
                                </span>
                                <span className="text-sm text-gray-600">
                                    Started: {new Date(trainingSession.startedAt).toLocaleTimeString()}
                                </span>
                            </div>
                            <span className="text-sm font-medium text-gray-700">
                                {trainingInteractions.length} interactions
                            </span>
                        </div>
                        <p className="text-sm text-blue-700">
                            Training mode active. Your interactions are being recorded for improvement.
                        </p>
                    </div>
                )}
            </div>

            <div className="flex-1 flex flex-col overflow-hidden bg-gray-50">
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] rounded-lg px-4 py-2 text-sm shadow-sm ${
                                    message.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-br-none'
                                        : 'bg-white text-gray-900 rounded-bl-none border border-gray-200'
                                } ${message.isError ? 'bg-red-50 border-red-200 text-red-900' : ''}`}
                            >
                                <div className="flex justify-between items-start mb-1 opacity-80">
                                    <span className="font-medium capitalize text-xs">
                                        {getRoleDisplay(message.role) || 'Agent'}
                                    </span>
                                    <span className="text-xs ml-2">
                                        {formatTimestamp(message.timestamp) || '00:00'}
                                    </span>
                                </div>
                                <div className="whitespace-pre-wrap leading-relaxed">
                                    {getMessageContent(message)}
                                </div>
                                {message.isError && (
                                    <div className="mt-1 flex items-center text-red-600 text-xs">
                                        <AlertCircle className="h-3 w-3 mr-1" />
                                        <span>Error sending message</span>
                                    </div>
                                )}
                                {message.reactions && message.reactions.length > 0 && (
                                    <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-gray-100/20">
                                        {message.reactions.map((reaction, index) => (
                                            <div key={index} className="flex items-center text-xs opacity-80">
                                                {reaction.type === 'like' && <ThumbsUp className="h-3 w-3 mr-1" />}
                                                {reaction.type === 'dislike' && <ThumbsDown className="h-3 w-3 mr-1" />}
                                                {reaction.type === 'flag' && <Flag className="h-3 w-3 mr-1" />}
                                                <span>{reaction.count}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {message.role === 'agent' && isTrainingMode && !message.isError && (
                                    <button
                                        onClick={() => handleProvideFeedback(message.id)}
                                        className="mt-2 flex items-center text-xs opacity-60 hover:opacity-100 transition-opacity"
                                        title="Provide feedback"
                                    >
                                        <Edit className="h-3 w-3 mr-1" />
                                        Provide Feedback
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                {feedbackTarget ? (
                    <div className="border-t p-4 bg-white shadow-lg">
                        <div className="flex items-center gap-2 mb-2 text-yellow-600">
                            <AlertTriangle className="h-4 w-4" />
                            <span className="text-sm font-medium">Provide feedback for this response:</span>
                        </div>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={currentFeedback}
                                onChange={(e) => setCurrentFeedback(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Enter your feedback..."
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                            <button
                                onClick={submitFeedback}
                                disabled={!currentFeedback.trim() || isLoading}
                                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                                aria-label="Submit feedback"
                            >
                                <Send className="h-4 w-4" />
                            </button>
                            <button
                                onClick={() => setFeedbackTarget(null)}
                                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                                aria-label="Cancel feedback"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="border-t p-4 bg-white">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleSendMessage()
                                }}
                                placeholder={isTrainingMode
                                    ? "Type your message to train the agent..."
                                    : "Type your message..."}
                                disabled={isLoading || (isTrainingMode && isPaused)}
                                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-50 disabled:text-gray-500"
                            />
                            <button
                                onClick={handleSendMessage}
                                disabled={!inputValue.trim() || isLoading || (isTrainingMode && isPaused)}
                                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                                aria-label="Send message"
                            >
                                <Send className="h-4 w-4" />
                            </button>
                        </div>
                        {isTrainingMode && isPaused && (
                            <div className="mt-2 text-center">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                    <Pause className="h-3 w-3 mr-1" />
                                    Training paused - resume to continue
                                </span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

// Helper components for better organization
// Add utility functions for formatting
const getRoleDisplay = (role: string) => {
    switch (role) {
        case 'user': return 'You'
        case 'agent': return 'Agent'
        case 'system': return 'System'
        default: return role
    }
}

const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getMessageContent = (message: ChatMessage) => {
    return message.content
}