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
  created_at: string
  updated_at: string
}

export interface UserOnboardingPayload {
  persona: UserPersona
  github_url?: string
  linkedin_url?: string
  role_title?: string
  company_name?: string
  industry?: string
  team_size?: string
  use_cases?: string[]
  tools_stack?: string[]
  primary_goal: string
}

export const useUserProfile = () => {
  const queryClient = useQueryClient()

  const profileQuery = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const response = await fetch('/api/v1/users/me/profile')
      if (!response.ok) {
        throw new Error('Failed to fetch user profile')
      }
      return response.json() as Promise<UserProfile>
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: async (payload: Partial<UserProfile>) => {
      const response = await fetch('/api/v1/users/me/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Failed to update user profile')
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
    },
  })

  const completeOnboardingMutation = useMutation({
    mutationFn: async (payload: UserOnboardingPayload) => {
      const response = await fetch('/api/v1/users/me/onboarding', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to complete onboarding')
      }
      return response.json() as Promise<UserProfile>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
    },
  })

  return {
    profile: profileQuery.data,
    loading: profileQuery.isLoading,
    error: profileQuery.error,
    refetch: profileQuery.refetch,
    updateProfile: updateProfileMutation.mutateAsync,
    updating: updateProfileMutation.isPending,
    completeOnboarding: completeOnboardingMutation.mutateAsync,
    completingOnboarding: completeOnboardingMutation.isPending,
  }
}

