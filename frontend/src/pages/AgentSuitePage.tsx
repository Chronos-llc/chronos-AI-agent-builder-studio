import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { conversationService, type Conversation, type ConversationAction, type ConversationDialogue, type ConversationMessage } from '../services/conversationService'
import { Progress } from '../components/ui/progress'

type SuiteTab = 'chat' | 'actions' | 'history' | 'settings' | 'fuzzy'

const AgentSuitePage = () => {
  const { id } = useParams()
  const agentId = Number(id)

  const [tab, setTab] = useState<SuiteTab>('chat')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [actions, setActions] = useState<ConversationAction[]>([])
  const [dialogues, setDialogues] = useState<ConversationDialogue[]>([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [newMessage, setNewMessage] = useState('')
  const [agenticPrompt, setAgenticPrompt] = useState('Plan this task internally before execution.')
  const [agenticError, setAgenticError] = useState<string | null>(null)

  useEffect(() => {
    const initialize = async () => {
      if (!Number.isFinite(agentId) || agentId <= 0) return
      setLoading(true)
      try {
        const list = await conversationService.listConversations(agentId)
        let conversation = list[0]
        if (!conversation) {
          conversation = await conversationService.createConversation(agentId)
        }
        setConversations(list.length ? list : [conversation])
        setActiveConversation(conversation)
      } finally {
        setLoading(false)
      }
    }
    initialize()
  }, [agentId])

  useEffect(() => {
    const loadConversationData = async () => {
      if (!activeConversation) return
      const [messagesData, actionsData, dialoguesData] = await Promise.all([
        conversationService.getMessages(activeConversation.id),
        conversationService.getActions(activeConversation.id),
        conversationService.getDialogues(activeConversation.id),
      ])
      setMessages(messagesData)
      setActions(actionsData)
      setDialogues(dialoguesData)
    }
    loadConversationData()
  }, [activeConversation])

  useEffect(() => {
    if (!activeConversation) return
    const timer = window.setInterval(async () => {
      const [messagesData, actionsData, dialoguesData] = await Promise.all([
        conversationService.getMessages(activeConversation.id),
        conversationService.getActions(activeConversation.id),
        conversationService.getDialogues(activeConversation.id),
      ])
      setMessages(messagesData)
      setActions(actionsData)
      setDialogues(dialoguesData)
    }, 5000)
    return () => window.clearInterval(timer)
  }, [activeConversation])

  const contextPercentage = useMemo(() => {
    if (!activeConversation || !activeConversation.context_tokens_max) return 0
    return Math.min(
      100,
      Math.round((activeConversation.context_tokens_used / activeConversation.context_tokens_max) * 100)
    )
  }, [activeConversation])

  const sendMessage = async () => {
    if (!activeConversation || !newMessage.trim()) return
    setSending(true)
    try {
      const message = await conversationService.sendMessage(activeConversation.id, newMessage.trim())
      setMessages(prev => [...prev, message])
      setNewMessage('')
      const refreshed = await conversationService.listConversations(agentId)
      const latest = refreshed.find(item => item.id === activeConversation.id)
      if (latest) {
        setActiveConversation(latest)
      }
    } finally {
      setSending(false)
    }
  }

  const continueOnWeb = async () => {
    if (!activeConversation) return
    const data = await conversationService.continueOnWeb(activeConversation.id)
    setMessages(data.messages)
  }

  const startAgenticThinking = async () => {
    if (!activeConversation) return
    setAgenticError(null)
    try {
      await conversationService.startAgenticThinking(agentId, activeConversation.id, agenticPrompt)
      const updatedDialogues = await conversationService.getDialogues(activeConversation.id)
      setDialogues(updatedDialogues)
    } catch (error: any) {
      setAgenticError(error?.message || 'Failed to start Agentic Thinking')
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="chronos-surface p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Agent Suite</h1>
            <p className="text-sm text-muted-foreground">Premium workspace for multi-channel execution history and live orchestration.</p>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn btn-secondary" onClick={continueOnWeb}>
              Continue Task On Web
            </button>
            <Link to={`/app/agents/${agentId}/edit`} className="btn btn-primary">
              Open Studio Settings
            </Link>
          </div>
        </div>
      </div>

      {activeConversation && (
        <div className="chronos-surface p-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Context Usage</span>
            <span className="text-muted-foreground">
              {activeConversation.context_tokens_used} / {activeConversation.context_tokens_max} tokens ({contextPercentage}%)
            </span>
          </div>
          <Progress 
            value={contextPercentage} 
            className="h-2 w-full rounded bg-muted"
            indicatorClassName="h-2 rounded bg-primary"
          />
          {activeConversation.context_summary && (
            <details className="rounded-md border border-border p-3">
              <summary className="cursor-pointer text-sm font-medium">Latest Context Summary</summary>
              <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{activeConversation.context_summary}</p>
            </details>
          )}
        </div>
      )}

      <div className="chronos-surface p-2">
        <div className="flex flex-wrap gap-2">
          {[
            { id: 'chat', label: 'Chat' },
            { id: 'actions', label: 'Tasks/Actions' },
            { id: 'history', label: 'History' },
            { id: 'settings', label: 'Settings' },
            { id: 'fuzzy', label: 'Fuzzy Edit' },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setTab(item.id as SuiteTab)}
              className={`rounded px-3 py-2 text-sm ${tab === item.id ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'chat' && (
        <div className="chronos-surface p-4 space-y-4">
          <div className="space-y-2 rounded border border-border p-3">
            <label className="block text-xs uppercase tracking-wide text-muted-foreground">Agentic Thinking (Experimental Beta)</label>
            <textarea
              className="input min-h-20 w-full"
              value={agenticPrompt}
              onChange={(e) => setAgenticPrompt(e.target.value)}
              placeholder="Prompt for internal dialogue planning"
            />
            <div className="flex items-center gap-2">
              <button className="btn btn-secondary" onClick={startAgenticThinking}>
                Start Agentic Thinking
              </button>
              {agenticError && <span className="text-xs text-red-400">{agenticError}</span>}
            </div>
            {dialogues.length > 0 && (
              <details>
                <summary className="cursor-pointer text-sm font-medium">Show Dialogue</summary>
                <div className="mt-2 space-y-2">
                  {dialogues.map(item => (
                    <div key={item.id} className="rounded border border-border p-2 text-sm">
                      <div className="text-xs uppercase text-muted-foreground">{item.role}</div>
                      <div>{item.content}</div>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>

          <div className="max-h-[420px] space-y-2 overflow-auto rounded border border-border p-3">
            {messages.map(message => (
              <div key={message.id} className={`rounded p-2 text-sm ${message.role === 'user' ? 'bg-primary/15' : 'bg-muted'}`}>
                <div className="text-xs uppercase text-muted-foreground">{message.role}</div>
                <div className="whitespace-pre-wrap">{message.content}</div>
              </div>
            ))}
            {messages.length === 0 && <div className="text-sm text-muted-foreground">No messages yet.</div>}
          </div>

          <div className="flex gap-2">
            <input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  sendMessage()
                }
              }}
              className="input w-full"
              placeholder="Type a message"
            />
            <button className="btn btn-primary" onClick={sendMessage} disabled={sending || !newMessage.trim()}>
              {sending ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      )}

      {tab === 'actions' && (
        <div className="chronos-surface p-4 space-y-2">
          {actions.length === 0 && <div className="text-sm text-muted-foreground">No actions logged yet.</div>}
          {actions.map(action => (
            <div key={action.id} className="rounded border border-border p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium">{action.action_type}</span>
                <span className="text-xs text-muted-foreground">{action.status}</span>
              </div>
              {action.payload?.stdout && (
                <pre className="mt-2 whitespace-pre-wrap text-xs">{String(action.payload.stdout)}</pre>
              )}
              {action.payload?.stderr && (
                <pre className="mt-2 whitespace-pre-wrap text-xs text-amber-300">{String(action.payload.stderr)}</pre>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === 'history' && (
        <div className="chronos-surface p-4 space-y-2">
          {conversations.map(conversation => (
            <button
              key={conversation.id}
              onClick={() => setActiveConversation(conversation)}
              className={`w-full rounded border p-3 text-left ${activeConversation?.id === conversation.id ? 'border-primary bg-primary/10' : 'border-border'}`}
            >
              <div className="font-medium">{conversation.title || `Conversation ${conversation.id}`}</div>
              <div className="text-xs text-muted-foreground">
                {conversation.channel_type} • {conversation.status} • {conversation.context_tokens_used}/{conversation.context_tokens_max}
              </div>
            </button>
          ))}
        </div>
      )}

      {tab === 'settings' && (
        <div className="chronos-surface p-4">
          <p className="text-sm text-muted-foreground">Agent configuration remains in Studio settings.</p>
          <Link to={`/app/agents/${agentId}/edit`} className="btn btn-primary mt-3 inline-flex">
            Open Bot Settings
          </Link>
        </div>
      )}

      {tab === 'fuzzy' && (
        <div className="chronos-surface p-4">
          <p className="text-sm text-muted-foreground">Use Fuzzy to edit architecture and orchestration behavior.</p>
          <Link to={`/app/agents/${agentId}/edit`} className="btn btn-secondary mt-3 inline-flex">
            Open In Studio (Fuzzy Tab)
          </Link>
        </div>
      )}
    </div>
  )
}

export default AgentSuitePage
