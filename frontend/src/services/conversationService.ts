const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_BASE = `${API_BASE_URL}/api/v1`

export interface Conversation {
  id: number
  agent_id: number
  user_id: number
  channel_type: string
  external_conversation_id?: string | null
  title?: string | null
  status: string
  last_message_at?: string | null
  context_summary?: string | null
  context_tokens_used: number
  context_tokens_max: number
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: number
  conversation_id: number
  role: 'user' | 'agent' | 'system'
  content: string
  metadata?: Record<string, any> | null
  tokens_estimate: number
  source_platform_message_id?: string | null
  created_at: string
  updated_at: string
}

export interface ConversationAction {
  id: number
  conversation_id: number
  action_type: string
  payload?: Record<string, any> | null
  status: string
  created_at: string
  updated_at: string
}

export interface ConversationDialogue {
  id: number
  conversation_id: number
  dialogue_id: string
  role: string
  content: string
  created_at: string
  updated_at: string
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

export const conversationService = {
  async createConversation(agentId: number): Promise<Conversation> {
    const response = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, channel_type: 'webchat' }),
    })
    return parseResponse<Conversation>(response)
  },

  async listConversations(agentId: number): Promise<Conversation[]> {
    const response = await fetch(`${API_BASE}/conversations?agent_id=${agentId}`)
    return parseResponse<Conversation[]>(response)
  },

  async getMessages(conversationId: number): Promise<ConversationMessage[]> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`)
    return parseResponse<ConversationMessage[]>(response)
  },

  async sendMessage(conversationId: number, content: string): Promise<ConversationMessage> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'user', content }),
    })
    return parseResponse<ConversationMessage>(response)
  },

  async getActions(conversationId: number): Promise<ConversationAction[]> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/actions`)
    return parseResponse<ConversationAction[]>(response)
  },

  async continueOnWeb(conversationId: number): Promise<{
    conversation_id: number
    context_summary?: string | null
    context_tokens_used: number
    context_tokens_max: number
    messages: ConversationMessage[]
  }> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/continue-on-web`, {
      method: 'POST',
    })
    return parseResponse(response)
  },

  async getDialogues(conversationId: number): Promise<ConversationDialogue[]> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/dialogues`)
    return parseResponse<ConversationDialogue[]>(response)
  },

  async startAgenticThinking(agentId: number, conversationId: number, prompt: string) {
    const response = await fetch(`${API_BASE}/agents/${agentId}/agentic-thinking/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: conversationId, prompt }),
    })
    return parseResponse(response)
  },
}

