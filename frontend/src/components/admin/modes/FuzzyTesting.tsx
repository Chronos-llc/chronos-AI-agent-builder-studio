import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../ui/card'
import { Button } from '../../ui/button'
import {
    Send,
    Trash2,
    Loader2,
    MessageSquare,
    Bot,
    User,
    Clock,
    Zap
} from 'lucide-react'
import { testFuzzyResponse, simulateFuzzyInteraction } from '../../../services/fuzzyService'
import type { FuzzyMessage, FuzzyTestResponse } from '../../../types/fuzzy'

interface TestMessage extends FuzzyMessage {
    testResponse?: FuzzyTestResponse
}

export const FuzzyTesting = () => {
    const [messages, setMessages] = useState<TestMessage[]>([])
    const [inputMessage, setInputMessage] = useState('')
    const [testing, setTesting] = useState(false)
    const [sessionContext, setSessionContext] = useState<Record<string, any>>({})

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || testing) return

        const userMessage: TestMessage = {
            id: Date.now(),
            role: 'user',
            content: inputMessage,
            timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, userMessage])
        setInputMessage('')
        setTesting(true)

        try {
            const response = await testFuzzyResponse({
                message: inputMessage,
                context: sessionContext
            })

            const assistantMessage: TestMessage = {
                id: Date.now() + 1,
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
                actions: response.actions_taken,
                testResponse: response
            }

            setMessages(prev => [...prev, assistantMessage])
        } catch (err) {
            const errorMessage: TestMessage = {
                id: Date.now() + 1,
                role: 'assistant',
                content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
                timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setTesting(false)
        }
    }

    const handleSimulateScenario = async (scenario: string) => {
        setTesting(true)

        try {
            const response = await simulateFuzzyInteraction(scenario, sessionContext)

            const simulationMessage: TestMessage = {
                id: Date.now(),
                role: 'assistant',
                content: `Simulation: ${scenario}\n\nResponse: ${response.response}`,
                timestamp: new Date().toISOString(),
                actions: response.actions_taken,
                testResponse: response
            }

            setMessages(prev => [...prev, simulationMessage])
        } catch (err) {
            const errorMessage: TestMessage = {
                id: Date.now(),
                role: 'assistant',
                content: `Simulation Error: ${err instanceof Error ? err.message : 'Failed to simulate'}`,
                timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setTesting(false)
        }
    }

    const handleClearConversation = () => {
        setMessages([])
        setSessionContext({})
    }

    const formatDuration = (ms: number): string => {
        if (ms < 1000) return `${ms.toFixed(0)}ms`
        return `${(ms / 1000).toFixed(2)}s`
    }

    const predefinedScenarios = [
        'Create a new customer support agent',
        'Add a web scraping tool to an existing agent',
        'Publish an agent to the marketplace',
        'Update agent instructions for better responses',
        'Configure Slack integration for an agent'
    ]

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">FUZZY Testing Interface</h2>
                    <p className="text-muted-foreground mt-1">
                        Test FUZZY's responses and simulate user interactions
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleClearConversation}
                    disabled={messages.length === 0}
                >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Clear Conversation
                </Button>
            </div>

            {/* Predefined Scenarios */}
            <Card>
                <CardHeader>
                    <CardTitle>Quick Test Scenarios</CardTitle>
                    <CardDescription>
                        Test common FUZZY interactions with predefined scenarios
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {predefinedScenarios.map((scenario, index) => (
                            <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                onClick={() => handleSimulateScenario(scenario)}
                                disabled={testing}
                                className="justify-start"
                            >
                                <Zap className="w-4 h-4 mr-2" />
                                {scenario}
                            </Button>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Conversation Area */}
            <Card>
                <CardHeader>
                    <CardTitle>Test Conversation</CardTitle>
                    <CardDescription>
                        Interact with FUZZY to test its responses
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Messages */}
                    <div className="space-y-4 mb-4 max-h-[500px] overflow-y-auto">
                        {messages.length === 0 ? (
                            <div className="text-center py-12 text-muted-foreground">
                                <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                <p>No messages yet. Start a conversation to test FUZZY.</p>
                            </div>
                        ) : (
                            messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                        }`}
                                >
                                    <div
                                        className={`flex gap-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                                            }`}
                                    >
                                        {/* Avatar */}
                                        <div
                                            className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.role === 'user'
                                                    ? 'bg-primary text-primary-foreground'
                                                    : 'bg-secondary text-secondary-foreground'
                                                }`}
                                        >
                                            {message.role === 'user' ? (
                                                <User className="w-4 h-4" />
                                            ) : (
                                                <Bot className="w-4 h-4" />
                                            )}
                                        </div>

                                        {/* Message Content */}
                                        <div className="flex-1">
                                            <div
                                                className={`rounded-lg p-3 ${message.role === 'user'
                                                        ? 'bg-primary text-primary-foreground'
                                                        : 'bg-muted'
                                                    }`}
                                            >
                                                <p className="whitespace-pre-wrap">{message.content}</p>
                                            </div>

                                            {/* Test Response Details */}
                                            {message.testResponse && (
                                                <div className="mt-2 space-y-2">
                                                    {/* Execution Stats */}
                                                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                                        <span className="flex items-center gap-1">
                                                            <Clock className="w-3 h-3" />
                                                            {formatDuration(message.testResponse.execution_time_ms)}
                                                        </span>
                                                        <span>
                                                            {message.testResponse.tokens_used} tokens
                                                        </span>
                                                        <span className={message.testResponse.success ? 'text-green-600' : 'text-red-600'}>
                                                            {message.testResponse.success ? 'Success' : 'Failed'}
                                                        </span>
                                                    </div>

                                                    {/* Actions Taken */}
                                                    {message.testResponse.actions_taken.length > 0 && (
                                                        <div className="bg-background border rounded-lg p-3">
                                                            <p className="text-sm font-medium mb-2">Actions Taken:</p>
                                                            <div className="space-y-1">
                                                                {message.testResponse.actions_taken.map((action, idx) => (
                                                                    <div key={idx} className="text-xs">
                                                                        <span className="font-medium">{action.action_name}</span>
                                                                        {action.description && (
                                                                            <span className="text-muted-foreground ml-2">
                                                                                - {action.description}
                                                                            </span>
                                                                        )}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Error Details */}
                                                    {message.testResponse.error && (
                                                        <div className="bg-destructive/10 border border-destructive rounded-lg p-3">
                                                            <p className="text-sm font-medium text-destructive">Error:</p>
                                                            <p className="text-xs text-destructive/80 mt-1">
                                                                {message.testResponse.error}
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            )}

                                            {/* Timestamp */}
                                            <p className="text-xs text-muted-foreground mt-1">
                                                {new Date(message.timestamp).toLocaleTimeString()}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}

                        {/* Loading Indicator */}
                        {testing && (
                            <div className="flex gap-3 justify-start">
                                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                                    <Bot className="w-4 h-4" />
                                </div>
                                <div className="bg-muted rounded-lg p-3">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className="flex gap-2">
                        <textarea
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleSendMessage()
                                }
                            }}
                            placeholder="Type a message to test FUZZY... (Shift+Enter for new line)"
                            className="flex-1 min-h-[80px] px-3 py-2 border border-input rounded-md bg-background resize-none"
                            disabled={testing}
                        />
                        <Button
                            onClick={handleSendMessage}
                            disabled={!inputMessage.trim() || testing}
                            className="self-end"
                        >
                            {testing ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Send className="w-4 h-4" />
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Context Editor */}
            <Card>
                <CardHeader>
                    <CardTitle>Session Context</CardTitle>
                    <CardDescription>
                        Add context data to simulate different scenarios
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <textarea
                        value={JSON.stringify(sessionContext, null, 2)}
                        onChange={(e) => {
                            try {
                                setSessionContext(JSON.parse(e.target.value))
                            } catch {
                                // Invalid JSON, ignore
                            }
                        }}
                        placeholder='{"user_id": 123, "agent_id": 456}'
                        className="w-full min-h-[120px] px-3 py-2 border border-input rounded-md bg-background font-mono text-sm"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                        Enter valid JSON to provide context for FUZZY interactions
                    </p>
                </CardContent>
            </Card>
        </div>
    )
}
