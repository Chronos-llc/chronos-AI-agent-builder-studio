import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export interface VirtualComputerConfig {
  id: number;
  agent_id: number;
  user_id: number;
  enabled: boolean;
  provider: 'e2b';
  idle_timeout_seconds: number;
  max_runtime_seconds: number;
  memory_mb: number;
  cpu_cores: number;
  allow_network: boolean;
  mcp_enabled: boolean;
  mcp_server_ids?: string[] | null;
  created_at: string;
  updated_at: string;
}

export const useVirtualComputerConfig = (agentId: number) => {
  const queryClient = useQueryClient();

  const configQuery = useQuery({
    queryKey: ['virtual-computer-config', agentId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/agents/${agentId}/virtual-computer`);
      if (!response.ok) {
        throw new Error('Failed to fetch virtual computer config');
      }
      return response.json() as Promise<VirtualComputerConfig>;
    }
  });

  const updateMutation = useMutation({
    mutationFn: async (updates: Partial<VirtualComputerConfig>) => {
      const response = await fetch(`/api/v1/agents/${agentId}/virtual-computer`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!response.ok) {
        throw new Error('Failed to update virtual computer config');
      }
      return response.json() as Promise<VirtualComputerConfig>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['virtual-computer-config', agentId] });
    }
  });

  const resetMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/agents/${agentId}/virtual-computer/reset`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Failed to reset virtual computer config');
      }
      return response.json() as Promise<VirtualComputerConfig>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['virtual-computer-config', agentId] });
    }
  });

  return {
    config: configQuery.data,
    isLoading: configQuery.isLoading,
    error: configQuery.error,
    updateConfig: updateMutation.mutateAsync,
    updating: updateMutation.isPending,
    resetConfig: resetMutation.mutateAsync,
    resetting: resetMutation.isPending
  };
};
