import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  AgentPhoneNumber,
  phoneNumberService,
  PhoneNumberOption,
  PhoneNumberProvider,
  PhoneNumberPurchaseRequest,
  PhoneNumberSearchRequest,
  PhoneProviderAvailability,
} from '../services/phoneNumberService'

export const useAgentPhoneNumbers = (agentId: number) => {
  const queryClient = useQueryClient()

  const providersQuery = useQuery<PhoneProviderAvailability[]>({
    queryKey: ['agent-phone-providers', agentId],
    queryFn: () => phoneNumberService.listProviders(agentId),
    enabled: Number.isFinite(agentId) && agentId > 0,
  })

  const ownedNumbersQuery = useQuery<AgentPhoneNumber[]>({
    queryKey: ['agent-phone-numbers', agentId],
    queryFn: () => phoneNumberService.listOwnedNumbers(agentId),
    enabled: Number.isFinite(agentId) && agentId > 0,
  })

  const searchMutation = useMutation<
    PhoneNumberOption[],
    Error,
    { provider: PhoneNumberProvider; payload: PhoneNumberSearchRequest }
  >({
    mutationFn: ({ provider, payload }) => phoneNumberService.searchNumbers(agentId, provider, payload),
  })

  const purchaseMutation = useMutation<
    AgentPhoneNumber,
    Error,
    { provider: PhoneNumberProvider; payload: PhoneNumberPurchaseRequest }
  >({
    mutationFn: ({ provider, payload }) => phoneNumberService.purchaseNumber(agentId, provider, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-phone-numbers', agentId] })
    },
  })

  const selectMutation = useMutation<AgentPhoneNumber, Error, { numberId: number }>({
    mutationFn: ({ numberId }) => phoneNumberService.selectNumber(agentId, numberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-phone-numbers', agentId] })
    },
  })

  return {
    providers: providersQuery.data || [],
    providersLoading: providersQuery.isLoading,
    providersError: providersQuery.error,
    ownedNumbers: ownedNumbersQuery.data || [],
    ownedNumbersLoading: ownedNumbersQuery.isLoading,
    ownedNumbersError: ownedNumbersQuery.error,
    searchResults: searchMutation.data || [],
    search: searchMutation.mutateAsync,
    searching: searchMutation.isPending,
    purchase: purchaseMutation.mutateAsync,
    purchasing: purchaseMutation.isPending,
    selectNumber: selectMutation.mutateAsync,
    selecting: selectMutation.isPending,
    refetchOwnedNumbers: ownedNumbersQuery.refetch,
  }
}

