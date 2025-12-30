import React, { useState, useEffect, useRef } from 'react'
import { io, Socket } from 'socket.io-client'
import { Send, User, Bot, Mic, MicOff, Video, VideoOff, Phone, PhoneOff, MoreVertical, Copy, Download, ThumbsUp, ThumbsDown, Flag, Share, Eye, EyeOff, AlertTriangle, Info, Check, X, Loader2, Play, Pause, Stop, SkipBack, SkipForward, Volume2, VolumeX, Settings, Trash2, Edit, Reply, Forward, Bookmark, Star, Smile, Paperclip, Image as ImageIcon, FileText } from 'lucide-react'

interface ChatMessage {
    id: string
    role: 'user' | 'agent' | 'system'
    content: string
    timestamp: string
    status: 'sent' | 'delivered' | 'read' | 'error'
    metadata?: any
    reactions?: { type: 'like' | 'dislike' | 'flag'; count: number; reactedByUser: boolean }[]
}

interface ChatTesterProps {
    agentId?: string
    initialMessages?: ChatMessage[]
    onSendMessage?: (message: string) => void
    onMessageReceived?: (message: ChatMessage) => void
    showVoiceInput?: boolean
    showVideoCall?: boolean
}

export const ChatTester: React.FC<ChatTesterProps> = ({
    agentId,
    initialMessages = [],
    onSendMessage,
    onMessageReceived,
    showVoiceInput = true,
    showVideoCall = true
}) => {
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
    const [newMessage, setNewMessage] = useState('')
    const [isConnected, setIsConnected] = useState(false)
    const [socket, setSocket] = useState<Socket | null>(null)
    const [isTyping, setIsTyping] = useState(false)
    const [isRecording, setIsRecording] = useState(false)
    const [isVideoCallActive, setIsVideoCallActive] = useState(false)
    const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'active' | 'ended'>('idle')
    const [showEmojiPicker, setShowEmojiPicker] = useState(false)
    const [showMessageActions, setShowMessageActions] = useState<string | null>(null)
    const [showSettings, setShowSettings] = useState(false)
    const [testMode, setTestMode] = useState<'chat' | 'emulator'>('chat')
    const [emulatorSpeed, setEmulatorSpeed] = useState(1)
    const [emulatorSteps, setEmulatorSteps] = useState<string[]>([])
    const [currentStep, setCurrentStep] = useState(0)
    const [isEmulatorRunning, setIsEmulatorRunning] = useState(false)

    const messagesEndRef = useRef<HTMLDivElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // Initialize WebSocket connection
    useEffect(() => {
        if (!agentId) return

        const newSocket = io(`ws://localhost:8000/agents/${agentId}/chat`, {
            transports: ['websocket'],
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        })

        setSocket(newSocket)

        newSocket.on('connect', () => {
            console.log('Connected to chat server')
            setIsConnected(true)
        })

        newSocket.on('disconnect', () => {
            console.log('Disconnected from chat server')
            setIsConnected(false)
        })

        newSocket.on('message', (message: ChatMessage) => {
            console.log('Received message:', message)
            setMessages(prev => [...prev, message])
            if (onMessageReceived) {
                onMessageReceived(message)
            }
        })

        newSocket.on('typing', (isTyping: boolean) => {
            setIsTyping(isTyping)
        })

        newSocket.on('error', (error: any) => {
            console.error('WebSocket error:', error)
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'system',
                content: `Error: ${error.message || 'Connection error'}`,
                timestamp: new Date().toISOString(),
                status: 'error'
            }])
        })

        return () => {
            newSocket.disconnect()
        }
    }, [agentId])

    // Handle sending messages
    const handleSendMessage = () => {
        if (!newMessage.trim() && !fileInputRef.current?.files?.length) return

        const messageContent = newMessage.trim()
        setNewMessage('')

        // Create user message
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: messageContent,
            timestamp: new Date().toISOString(),
            status: 'sent'
        }

        setMessages(prev => [...prev, userMessage])

        // Send to server if connected
        if (socket && isConnected) {
            socket.emit('message', {
                content: messageContent,
                agentId,
                metadata: {
                    timestamp: new Date().toISOString(),
                    type: 'text'
                }
            })
        } else {
            // Simulate agent response if not connected
            setTimeout(() => {
                const agentMessage: ChatMessage = {
                    id: (Date.now() + 1).toString(),
                    role: 'agent',
                    content: `I received your message: "${messageContent}". This is a simulated response since the WebSocket connection is not active.`,
                    timestamp: new Date().toISOString(),
                    status: 'delivered'
                }
                setMessages(prev => [...prev, agentMessage])
                if (onMessageReceived) {
                    onMessageReceived(agentMessage)
                }
            }, 1000)
        }

        if (onSendMessage) {
            onSendMessage(messageContent)
        }
    }

    // Handle file upload
    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return
n
        const file = files[0]
        const reader = new FileReader()

        reader.onload = (event) => {
            const content = event.target?.result as string
            const fileMessage: ChatMessage = {
                id: Date.now().toString(),
                role: 'user',
                content: `[File: ${file.name}] ${content.substring(0, 100)}...`,
                timestamp: new Date().toISOString(),
                status: 'sent',
                metadata: {
                    fileType: file.type,
                    fileName: file.name,
                    fileSize: file.size
                }
            }

            setMessages(prev => [...prev, fileMessage])

            // Simulate agent response for file
            setTimeout(() => {
                const agentMessage: ChatMessage = {
                    id: (Date.now() + 1).toString(),
                    role: 'agent',
                    content: `I've received the file "${file.name}" (${(file.size / 1024).toFixed(1)} KB). The content has been processed and added to the knowledge base.`,
                    timestamp: new Date().toISOString(),
                    status: 'delivered'
                }
                setMessages(prev => [...prev, agentMessage])
            }, 1500)
        }

        if (file.type.startsWith('text/')) {
            reader.readAsText(file)
        } else {
            reader.readAsDataURL(file)
        }
    }

    // Handle voice input toggle
    const toggleVoiceInput = () => {
        if (isRecording) {
            // Stop recording
            setIsRecording(false)
            // In a real implementation, this would stop the media recorder
        } else {
            // Start recording
            setIsRecording(true)
            // In a real implementation, this would start the media recorder
            setTimeout(() => {
                // Simulate voice input result
                const voiceMessage: ChatMessage = {
                    id: Date.now().toString(),
                    role: 'user',
                    content: 'This is a simulated voice input message.',
                    timestamp: new Date().toISOString(),
                    status: 'sent',
                    metadata: {
                        inputType: 'voice',
                        duration: 3.5
                    }
                }
                setMessages(prev => [...prev, voiceMessage])
                setIsRecording(false)
            }, 3000)
        }
    }

    // Handle video call toggle
    const toggleVideoCall = () => {
        if (isVideoCallActive) {
            // End call
            setCallStatus('ended')
            setTimeout(() => {
                setIsVideoCallActive(false)
                setCallStatus('idle')
            }, 1000)
        } else {
            // Start call
            setCallStatus('connecting')
            setIsVideoCallActive(true)
            setTimeout(() => {
                setCallStatus('active')
            }, 2000)
        }
    }

    // Handle message reactions
    const handleReaction = (messageId: string, reactionType: 'like' | 'dislike' | 'flag') => {
        setMessages(prev => prev.map(message => {
            if (message.id === messageId) {
                const existingReaction = message.reactions?.find(r => r.type === reactionType)
                let updatedReactions = message.reactions || []

                if (existingReaction) {
                    // Toggle reaction
                    updatedReactions = updatedReactions.map(r =>
                        r.type === reactionType ? {
                            ...r,
                            count: existingReaction.reactedByUser ? r.count - 1 : r.count + 1,
                            reactedByUser: !existingReaction.reactedByUser
                        } : r
                    )
                } else {
                    // Add new reaction
                    updatedReactions.push({
                        type: reactionType,
                        count: 1,
                        reactedByUser: true
                    })
                }

                return { ...message, reactions: updatedReactions }
            }
            return message
        }))
    }

    // Handle emulator controls
    const startEmulator = () => {
        if (isEmulatorRunning) return

        setIsEmulatorRunning(true)
        setCurrentStep(0)

        // Simulate emulator steps
        const steps = [
            'Initializing agent...',
            'Loading system prompt...',
            'Processing knowledge base...',
            'Setting up tools and integrations...',
            'Establishing WebSocket connection...',
            'Agent ready for testing!'
        ]

        setEmulatorSteps(steps)

        steps.forEach((step, index) => {
            setTimeout(() => {
                setCurrentStep(index + 1)
                
                if (index === steps.length - 1) {
                    setTimeout(() => {
                        setIsEmulatorRunning(false)
                        
                        // Add system message
                        const systemMessage: ChatMessage = {
                            id: Date.now().toString(),
                            role: 'system',
                            content: 'Emulator test completed successfully! Agent is ready for real-time testing.',
                            timestamp: new Date().toISOString(),
                            status: 'delivered'
                        }
                        setMessages(prev => [...prev, systemMessage])
                    }, 1000)
                }
            }, index * (3000 / emulatorSpeed))
        })
    }

    const pauseEmulator = () => {
        setIsEmulatorRunning(false)
    }

    const stopEmulator = () => {
        setIsEmulatorRunning(false)
        setCurrentStep(0)
        setEmulatorSteps([])
    }

    // Format timestamp
    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    // Get role display name
    const getRoleDisplay = (role: ChatMessage['role']) => {
        switch (role) {
            case 'user': return 'You'
            case 'agent': return 'Agent'
            case 'system': return 'System'
            default: return role
        }
    }

    // Get role icon
    const getRoleIcon = (role: ChatMessage['role']) => {
        switch (role) {
            case 'user': return <User className="w-4 h-4" />
            case 'agent': return <Bot className="w-4 h-4" />
            case 'system': return <Info className="w-4 h-4" />
            default: return <User className="w-4 h-4" />
        }
    }

    // Get role color
    const getRoleColor = (role: ChatMessage['role']) => {
        switch (role) {
            case 'user': return 'bg-primary text-primary-foreground'
            case 'agent': return 'bg-secondary'
            case 'system': return 'bg-muted'
            default: return 'bg-primary text-primary-foreground'
        }
    }

    return (
        <div className="flex flex-col h-full bg-background">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-border bg-card">
                <div className="flex items-center gap-4">
                    <button
                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${testMode === 'chat' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        onClick={() => setTestMode('chat')}
                        disabled={isEmulatorRunning}
                    >
                        <Send className="w-4 h-4" />
                        <span>Chat Mode</span>
                    </button>
                    <button
                        className={`flex items-center gap-2 px-3 py-1 rounded-md ${testMode === 'emulator' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        onClick={() => setTestMode('emulator')}
                        disabled={isEmulatorRunning}
                    >
                        <Cpu className="w-4 h-4" />
                        <span>Emulator Mode</span>
                    </button>
                </div>

                <div className="flex items-center gap-2">
                    {/* Connection status */}
                    <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-xs text-muted-foreground">
                            {isConnected ? 'Connected' : 'Offline (simulated)'}
                        </span>
                    </div>

                    {/* Settings */}
                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className="p-1 rounded-md hover:bg-accent"
                        title="Settings"
                    >
                        <Settings className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Emulator Controls */}
            {testMode === 'emulator' && (
                <div className="p-3 border-b border-border bg-secondary">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <span className="text-sm text-muted-foreground">Speed:</span>
                                <select
                                    value={emulatorSpeed}
                                    onChange={(e) => setEmulatorSpeed(Number(e.target.value))}
                                    className="px-2 py-1 border border-input rounded-md bg-background text-foreground text-sm"
                                    disabled={isEmulatorRunning}
                                >
                                    <option value={0.5}>0.5x (Slow)</option>
                                    <option value={1}>1x (Normal)</option>
                                    <option value={2}>2x (Fast)</option>
                                    <option value={5}>5x (Very Fast)</option>
                                </select>
                            </div>

                            {isEmulatorRunning && (
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-muted-foreground">Progress:</span>
                                    <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary"
                                            style={{ width: `${(currentStep / Math.max(emulatorSteps.length, 1)) * 100}%` }}
                                        />
                                    </div>
                                    <span className="text-xs text-muted-foreground">
                                        {currentStep}/{emulatorSteps.length}
                                    </span>
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-2">
                            {!isEmulatorRunning ? (
                                <button
                                    onClick={startEmulator}
                                    className="flex items-center gap-2 px-3 py-1 bg-green-500 text-white rounded-md hover:bg-green-600"
                                    disabled={isEmulatorRunning}
                                >
                                    <Play className="w-4 h-4" />
                                    <span>Start Emulator</span>
                                </button>
                            ) : (
                                <>
                                    <button
                                        onClick={pauseEmulator}
                                        className="flex items-center gap-2 px-3 py-1 bg-yellow-500 text-white rounded-md hover:bg-yellow-600"
                                    >
                                        <Pause className="w-4 h-4" />
                                        <span>Pause</span>
                                    </button>
                                    <button
                                        onClick={stopEmulator}
                                        className="flex items-center gap-2 px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600"
                                    >
                                        <Stop className="w-4 h-4" />
                                        <span>Stop</span>
                                    </button>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Emulator Steps */}
                    {isEmulatorRunning && emulatorSteps.length > 0 && (
                        <div className="mt-3 p-2 bg-card rounded-md text-sm">
                            <div className="font-medium mb-1">Current Step:</div>
                            <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${currentStep <= emulatorSteps.length ? 'bg-primary' : 'bg-muted'}`} />
                                <span>{emulatorSteps[currentStep - 1] || 'Completed'}</span>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                        <Send className="w-8 h-8 mx-auto mb-2" />
                        <p>No messages yet</p>
                        <p className="text-sm mt-1">Start a conversation to test your agent</p>
                    </div>
                ) : (
                    messages.map(message => (
                        <div
                            key={message.id}
                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] p-3 rounded-lg relative group ${getRoleColor(message.role)} ${message.role === 'user' ? 'rounded-br-none' : message.role === 'agent' ? 'rounded-bl-none' : 'rounded-lg'}`}
                            >
                                {/* Message Header */}
                                <div className="flex items-center justify-between mb-1">
                                    <div className="flex items-center gap-2">
                                        {getRoleIcon(message.role)}
                                        <span className="font-medium capitalize text-xs">{getRoleDisplay(message.role)}</span>
                                        <span className="text-xs text-muted-foreground">
                                            {formatTimestamp(message.timestamp)}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => setShowMessageActions(showMessageActions === message.id ? null : message.id)}
                                        className="p-1 rounded-md hover:bg-accent/50 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <MoreVertical className="w-3 h-3" />
                                    </button>
                                </div>

                                {/* Message Content */}
                                <div className="whitespace-pre-wrap break-words">
                                    {message.content}
                                </div>

                                {/* Message Metadata */}
                                {message.metadata && (
                                    <div className="mt-2 text-xs text-muted-foreground border-t border-border/50 pt-2">
                                        <div className="font-medium mb-1">Metadata:</div>
                                        <div className="grid grid-cols-2 gap-1">
                                            {Object.entries(message.metadata).map(([key, value]) => (
                                                <div key={key} className="flex justify-between">
                                                    <span className="text-muted-foreground">{key}:</span>
                                                    <span className="truncate max-w-[100px]">{String(value)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Message Status */}
                                {message.status !== 'delivered' && (
                                    <div className="flex items-center gap-1 text-xs mt-2">
                                        {message.status === 'sent' && (
                                            <>
                                                <Loader2 className="w-3 h-3 animate-spin" />
                                                <span>Sending...</span>
                                            </>
                                        )}
                                        {message.status === 'read' && (
                                            <>
                                                <Check className="w-3 h-3 text-blue-500" />
                                                <span>Read</span>
                                            </>
                                        )}
                                        {message.status === 'error' && (
                                            <>
                                                <AlertTriangle className="w-3 h-3 text-red-500" />
                                                <span>Failed to send</span>
                                            </>
                                        )}
                                    </div>
                                )}

                                {/* Message Actions */}
                                {showMessageActions === message.id && (
                                    <div className="absolute top-full right-0 mt-1 w-48 bg-card border border-border rounded-md shadow-lg z-10">
                                        <button
                                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent w-full text-left"
                                            onClick={() => {
                                                navigator.clipboard.writeText(message.content)
                                                setShowMessageActions(null)
                                            }}
                                        >
                                            <Copy className="w-3 h-3" />
                                            <span>Copy</span>
                                        </button>
                                        <button
                                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent w-full text-left"
                                            onClick={() => {
                                                // Download functionality would go here
                                                setShowMessageActions(null)
                                            }}
                                        >
                                            <Download className="w-3 h-3" />
                                            <span>Download</span>
                                        </button>
                                        <button
                                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent w-full text-left"
                                            onClick={() => {
                                                // Reply functionality
                                                setNewMessage(`@${getRoleDisplay(message.role)} ${message.content} `)
                                                setShowMessageActions(null)
                                            }}
                                        >
                                            <Reply className="w-3 h-3" />
                                            <span>Reply</span>
                                        </button>
                                        <button
                                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent w-full text-left"
                                            onClick={() => {
                                                // Forward functionality
                                                setShowMessageActions(null)
                                            }}
                                        >
                                            <Forward className="w-3 h-3" />
                                            <span>Forward</span>
                                        </button>
                                        <button
                                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent w-full text-left"
                                            onClick={() => {
                                                // Bookmark functionality
                                                setShowMessageActions(null)
                                            }}
                                        >
                                            <Bookmark className="w-3 h-3" />
                                            <span>Bookmark</span>
                                        </button>
                                        <button
                                            className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent w-full text-left"
                                            onClick={() => {
                                                // Delete functionality
                                                setMessages(prev => prev.filter(m => m.id !== message.id))
                                                setShowMessageActions(null)
                                            }}
                                        >
                                            <Trash2 className="w-3 h-3" />
                                            <span>Delete</span>
                                        </button>
                                    </div>
                                )}

                                {/* Message Reactions */}
                                <div className="flex items-center gap-1 mt-2 pt-2 border-t border-border/50">
                                    <button
                                        onClick={() => handleReaction(message.id, 'like')}
                                        className={`p-1 rounded-md hover:bg-accent/50 ${message.reactions?.some(r => r.type === 'like' && r.reactedByUser) ? 'text-blue-500' : ''}`}
                                    >
                                        <ThumbsUp className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => handleReaction(message.id, 'dislike')}
                                        className={`p-1 rounded-md hover:bg-accent/50 ${message.reactions?.some(r => r.type === 'dislike' && r.reactedByUser) ? 'text-red-500' : ''}`}
                                    >
                                        <ThumbsDown className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => handleReaction(message.id, 'flag')}
                                        className={`p-1 rounded-md hover:bg-accent/50 ${message.reactions?.some(r => r.type === 'flag' && r.reactedByUser) ? 'text-yellow-500' : ''}`}
                                    >
                                        <Flag className="w-3 h-3" />
                                    </button>

                                    {message.reactions && message.reactions.length > 0 && (
                                        <div className="flex items-center gap-1 ml-2">
                                            {message.reactions.map(reaction => (
                                                reaction.count > 0 && (
                                                    <span key={reaction.type} className="text-xs flex items-center gap-1">
                                                        {reaction.type === 'like' && <ThumbsUp className="w-3 h-3" />}
                                                        {reaction.type === 'dislike' && <ThumbsDown className="w-3 h-3" />}
                                                        {reaction.type === 'flag' && <Flag className="w-3 h-3" />}
                                                        {reaction.count}
                                                    </span>
                                                )
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Typing Indicator */}
            {isTyping && (
                <div className="p-2 bg-card border-t border-border">
                    <div className="flex items-center gap-2">
                        <Bot className="w-4 h-4" />
                        <span className="text-sm text-muted-foreground">Agent is typing</span>
                        <div className="flex gap-1">
                            <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                            <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            <div className="w-1 h-1 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                        </div>
                    </div>
                </div>
            )}

            {/* Input Area */}
            <div className="border-t border-border p-3 bg-card">
                <div className="flex items-end gap-2">
                    {/* File upload */}
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="p-2 rounded-md hover:bg-accent"
                        title="Upload file"
                    >
                        <Paperclip className="w-5 h-5" />
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            onChange={handleFileUpload}
                            accept="*"
                        />
                    </button>

                    {/* Emoji picker */}
                    <button
                        onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                        className="p-2 rounded-md hover:bg-accent"
                        title="Emoji"
                    >
                        <Smile className="w-5 h-5" />
                    </button>

                    {/* Voice input */}
                    {showVoiceInput && (
                        <button
                            onClick={toggleVoiceInput}
                            className={`p-2 rounded-md ${isRecording ? 'bg-red-500 text-white' : 'hover:bg-accent'}`}
                            title={isRecording ? 'Stop recording' : 'Start voice input'}
                        >
                            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                        </button>
                    )}

                    {/* Video call */}
                    {showVideoCall && (
                        <button
                            onClick={toggleVideoCall}
                            className={`p-2 rounded-md ${isVideoCallActive ? 'bg-green-500 text-white' : 'hover:bg-accent'}`}
                            title={isVideoCallActive ? 'End video call' : 'Start video call'}
                            disabled={callStatus === 'connecting'}
                        >
                            {isVideoCallActive ? <PhoneOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                        </button>
                    )}

                    {/* Message input */}
                    <div className="flex-1 relative">
                        <textarea
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            onKeyPress={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleSendMessage()
                                }
                            }}
                            placeholder="Type your message..."
                            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground min-h-[40px] max-h-[120px] resize-none"
                            rows={1}
                        />
                        {showEmojiPicker && (
                            <div className="absolute bottom-full left-0 mb-1 bg-card border border-border rounded-md p-2 shadow-lg z-20">
                                <div className="text-sm mb-2">Emoji picker coming soon!</div>
                                <div className="grid grid-cols-6 gap-1">
                                    {['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊'].map((emoji, index) => (
                                        <button
                                            key={index}
                                            onClick={() => {
                                                setNewMessage(prev => prev + emoji)
                                                setShowEmojiPicker(false)
                                            }}
                                            className="p-1 hover:bg-accent rounded"
                                        >
                                            {emoji}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Send button */}
                    <button
                        onClick={handleSendMessage}
                        disabled={!newMessage.trim() && !fileInputRef.current?.files?.length}
                        className="p-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                        title="Send message (Enter)"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>

                <div className="text-xs text-muted-foreground mt-1 flex justify-between">
                    <span>Press Enter to send</span>
                    <span>{newMessage.length} characters</span>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-md">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Settings className="w-4 h-4" />
                                <span>Chat Settings</span>
                            </h3>
                            <button
                                onClick={() => setShowSettings(false)}
                                className="p-1 rounded-md hover:bg-accent"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="p-4 space-y-4">
                            <div>
                                <h4 className="font-medium mb-2">General Settings</h4>
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2">
                                        <input
                                            type="checkbox"
                                            checked={showVoiceInput}
                                            onChange={(e) => setShowVoiceInput(e.target.checked)}
                                            className="rounded"
                                        />
                                        <span className="text-sm">Enable voice input</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input
                                            type="checkbox"
                                            checked={showVideoCall}
                                            onChange={(e) => setShowVideoCall(e.target.checked)}
                                            className="rounded"
                                        />
                                        <span className="text-sm">Enable video calls</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" className="rounded" />
                                        <span className="text-sm">Enable message reactions</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Show typing indicators</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <h4 className="font-medium mb-2">Message Settings</h4>
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Show timestamps</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Show message status</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" className="rounded" />
                                        <span className="text-sm">Show metadata</span>
                                    </label>
                                </div>
                            </div>

                            <div>
                                <h4 className="font-medium mb-2">Advanced</h4>
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" className="rounded" />
                                        <span className="text-sm">Enable WebSocket compression</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Enable message encryption</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" className="rounded" />
                                        <span className="text-sm">Enable debug logging</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowSettings(false)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Close
                            </button>
                            <button
                                onClick={() => {
                                    setShowSettings(false)
                                    toast.success('Settings saved')
                                }}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                Save Settings
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Video Call Modal */}
            {isVideoCallActive && (
                <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl h-[80vh] flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Video className="w-4 h-4" />
                                <span>Video Call</span>
                            </h3>
                            <div className="flex items-center gap-2">
                                <span className="text-sm text-muted-foreground">
                                    {callStatus === 'connecting' ? 'Connecting...' : callStatus === 'active' ? 'Call active' : 'Ending call...'}
                                </span>
                                <button
                                    onClick={toggleVideoCall}
                                    className="p-1 rounded-md hover:bg-accent"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 flex items-center justify-center bg-muted">
                            {callStatus === 'connecting' ? (
                                <div className="flex flex-col items-center gap-4">
                                    <Loader2 className="w-8 h-8 animate-spin" />
                                    <span>Connecting to agent...</span>
                                </div>
                            ) : callStatus === 'active' ? (
                                <div className="flex flex-col items-center gap-4">
                                    <div className="w-32 h-32 bg-gray-300 rounded-full flex items-center justify-center">
                                        <Bot className="w-16 h-16 text-gray-600" />
                                    </div>
                                    <div className="text-center">
                                        <h4 className="font-medium">Agent Video Call</h4>
                                        <p className="text-sm text-muted-foreground">Video call simulation</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-4">
                                    <PhoneOff className="w-8 h-8 text-red-500" />
                                    <span>Call ended</span>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-border p-4 flex justify-center gap-4">
                            <button
                                className="p-2 rounded-full bg-red-500 text-white hover:bg-red-600"
                                onClick={toggleVideoCall}
                                title="End call"
                            >
                                <PhoneOff className="w-5 h-5" />
                            </button>
                            <button
                                className="p-2 rounded-full bg-muted hover:bg-accent"
                                title="Mute microphone"
                            >
                                <MicOff className="w-5 h-5" />
                            </button>
                            <button
                                className="p-2 rounded-full bg-muted hover:bg-accent"
                                title="Turn off camera"
                            >
                                <VideoOff className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}