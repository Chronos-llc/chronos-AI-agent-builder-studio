import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

export type UserPersona = 'developer' | 'power_user' | 'enterprise'

export interface UserProfile {
  id: number
  user_id: number
  persona?: UserPersona
  github_url?: string | null
  linkedin_url?: string | null
  role_title?: string | null
  company_name?: string | null
  industry?: string | null
  team_size?: string | null
  use_cases?: string[] | null
  tools_stack?: string[] | null
  primary_goal?: string | null
  onboarding_completed: boolean
  fuzzy_onboarding_state?: 'pending' | 'completed' | 'skipped'
  fuzzy_onboarding_completed_at?: string | null
  fuzzy_onboarding_skipped_at?: string | null
  created_at: string
  updated_at: string
}

export interface ProfileOnboardingPayload {
  persona: UserPersona
  github_url?: string
  linkedin_url?: string
  role_title?: string
  company_name?: string
  industry?: string
  team_size?: string
}

export interface FuzzyOnboardingPayload {
  primary_goal: string
  use_cases?: string[]
  tools_stack?: string[]
}

export interface UserOnboardingPayload extends ProfileOnboardingPayload, FuzzyOnboardingPayload {}

export interface UserOnboardingStatus {
  onboarding_completed: boolean
  fuzzy_onboarding_state: 'pending' | 'completed' | 'skipped'
  fuzzy_onboarding_completed_at?: string | null
  fuzzy_onboarding_skipped_at?: string | null
  profile: UserProfile
}

const API_BASE_URL_RAW = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const API_BASE_URL = API_BASE_URL_RAW.replace(/\/$/, '')

const getAccessToken = () =>
  localStorage.getItem('chronos_access_token') || localStorage.getItem('access_token')

const buildHeaders = (withJsonContentType = false): HeadersInit => {
  const token = getAccessToken()
  const headers: Record<string, string> = {}
  if (withJsonContentType) {
    headers['Content-Type'] = 'application/json'
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  return headers
}

const parseError = async (response: Response, fallback: string) => {
  try {
    const data = await response.json()
    if (typeof data?.detail === 'string') {
      return data.detail
    }
  } catch {
    // no-op
  }
  return fallback
}

export const useUserProfile = () => {
  const queryClient = useQueryClient()

  const profileQuery = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/profile`, {
        credentials: 'include',
        headers: buildHeaders(),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to fetch user profile'))
      }
      return response.json() as Promise<UserProfile>
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: async (payload: Partial<UserProfile>) => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/profile`, {
        method: 'PUT',
        credentials: 'include',
        headers: buildHeaders(true),
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to update user profile'))
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
    },
  })

  const completeOnboardingMutation = useMutation({
    mutationFn: async (payload: UserOnboardingPayload) => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/onboarding`, {
        method: 'POST',
        credentials: 'include',
        headers: buildHeaders(true),
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to complete onboarding'))
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
    },
  })

  const completeProfileOnboardingMutation = useMutation({
    mutationFn: async (payload: ProfileOnboardingPayload) => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/onboarding/profile`, {
        method: 'POST',
        credentials: 'include',
        headers: buildHeaders(true),
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to complete profile onboarding'))
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      queryClient.invalidateQueries({ queryKey: ['user-onboarding-status'] })
    },
  })

  const completeFuzzyOnboardingMutation = useMutation({
    mutationFn: async (payload: FuzzyOnboardingPayload) => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/onboarding/fuzzy`, {
        method: 'POST',
        credentials: 'include',
        headers: buildHeaders(true),
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to complete fuzzy onboarding'))
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      queryClient.invalidateQueries({ queryKey: ['user-onboarding-status'] })
    },
  })

  const skipFuzzyOnboardingMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/onboarding/fuzzy/skip`, {
        method: 'POST',
        credentials: 'include',
        headers: buildHeaders(true),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to skip fuzzy onboarding'))
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      queryClient.invalidateQueries({ queryKey: ['user-onboarding-status'] })
    },
  })

  const onboardingStatusQuery = useQuery({
    queryKey: ['user-onboarding-status'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/me/onboarding/status`, {
        credentials: 'include',
        headers: buildHeaders(),
      })
      if (!response.ok) {
        throw new Error(await parseError(response, 'Failed to fetch onboarding status'))
      }
      return response.json() as Promise<UserOnboardingStatus>
    },
  })

  return {
    profile: profileQuery.data,
    loading: profileQuery.isLoading,
    error: profileQuery.error,
    refetch: profileQuery.refetch,
    onboardingStatus: onboardingStatusQuery.data,
    onboardingStatusLoading: onboardingStatusQuery.isLoading,
    updateProfile: updateProfileMutation.mutateAsync,
    updating: updateProfileMutation.isPending,
    completeOnboarding: completeOnboardingMutation.mutateAsync,
    completingOnboarding: completeOnboardingMutation.isPending,
    completeProfileOnboarding: completeProfileOnboardingMutation.mutateAsync,
    completingProfileOnboarding: completeProfileOnboardingMutation.isPending,
    completeFuzzyOnboarding: completeFuzzyOnboardingMutation.mutateAsync,
    completingFuzzyOnboarding: completeFuzzyOnboardingMutation.isPending,
    skipFuzzyOnboarding: skipFuzzyOnboardingMutation.mutateAsync,
    skippingFuzzyOnboarding: skipFuzzyOnboardingMutation.isPending,
  }
}
