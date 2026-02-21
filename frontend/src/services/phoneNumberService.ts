export type PhoneNumberProvider = 'twilio' | 'vonage'

export interface PhoneProviderAvailability {
  provider: PhoneNumberProvider
  configured: boolean
  available: boolean
  message?: string | null
}

export interface PhoneNumberSearchRequest {
  country_code: string
  capabilities: string[]
  limit?: number
  contains?: string
}

export interface PhoneNumberOption {
  provider: PhoneNumberProvider
  provider_number_id: string
  phone_number_e164: string
  country_code?: string | null
  capabilities: string[]
  monthly_cost?: number | null
  currency?: string | null
  metadata?: Record<string, unknown> | null
}

export interface PhoneNumberPurchaseRequest {
  country_code: string
  phone_number_e164: string
  provider_number_id?: string | null
  capabilities: string[]
  confirm_purchase: boolean
}

export interface AgentPhoneNumber {
  id: number
  agent_id: number
  provider: PhoneNumberProvider
  phone_number_e164: string
  provider_number_id: string
  country_code?: string | null
  capabilities: string[]
  monthly_cost?: number | null
  currency: string
  is_selected: boolean
  status: string
  metadata?: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

const authHeaders = (): HeadersInit => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const handleJson = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    const detail = payload?.detail || 'Request failed'
    throw new Error(detail)
  }
  return response.json() as Promise<T>
}

export const phoneNumberService = {
  async listProviders(agentId: number): Promise<PhoneProviderAvailability[]> {
    const response = await fetch(`/api/v1/agents/${agentId}/phone/providers`, {
      headers: {
        ...authHeaders(),
      },
    })
    return handleJson<PhoneProviderAvailability[]>(response)
  },

  async searchNumbers(
    agentId: number,
    provider: PhoneNumberProvider,
    payload: PhoneNumberSearchRequest
  ): Promise<PhoneNumberOption[]> {
    const response = await fetch(`/api/v1/agents/${agentId}/phone/providers/${provider}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    })
    return handleJson<PhoneNumberOption[]>(response)
  },

  async purchaseNumber(
    agentId: number,
    provider: PhoneNumberProvider,
    payload: PhoneNumberPurchaseRequest
  ): Promise<AgentPhoneNumber> {
    const response = await fetch(`/api/v1/agents/${agentId}/phone/providers/${provider}/purchase`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    })
    return handleJson<AgentPhoneNumber>(response)
  },

  async listOwnedNumbers(agentId: number): Promise<AgentPhoneNumber[]> {
    const response = await fetch(`/api/v1/agents/${agentId}/phone/numbers`, {
      headers: {
        ...authHeaders(),
      },
    })
    return handleJson<AgentPhoneNumber[]>(response)
  },

  async selectNumber(agentId: number, numberId: number): Promise<AgentPhoneNumber> {
    const response = await fetch(`/api/v1/agents/${agentId}/phone/numbers/${numberId}/select`, {
      method: 'POST',
      headers: {
        ...authHeaders(),
      },
    })
    return handleJson<AgentPhoneNumber>(response)
  },
}

