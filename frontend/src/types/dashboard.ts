export interface AgentHomeCard {
  id: number
  name: string
  status: string
  created_at: string
  updated_at: string
  last_message_at: string | null
  deployed_channels: string[]
  messages_received: number
  errors_encountered: number
}

export interface AgentHomeCardsResponse {
  generated_at: string
  workspace_name: string
  plan: string
  agents: AgentHomeCard[]
}

