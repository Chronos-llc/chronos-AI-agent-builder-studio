"use client"

import React, { useState } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Checkbox } from '../ui/checkbox'
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription, 
  DialogFooter 
} from '../ui/dialog'
import { toast } from '../ui/use-toast'
import { useMarketplace } from '../../hooks/useMarketplace'
import { Loader2 } from 'lucide-react'

interface AgentCopyModalProps {
  isOpen: boolean
  onClose: () => void
  listingId: number
  listingTitle: string
  originalAgentName: string
  onCopySuccess: (agentId: number) => void
}

export default function AgentCopyModal({ 
  isOpen, 
  onClose, 
  listingId, 
  listingTitle, 
  originalAgentName, 
  onCopySuccess 
}: AgentCopyModalProps) {
  const [customName, setCustomName] = useState<string>(`${originalAgentName} (Copy)`)
  const [preserveReference, setPreserveReference] = useState<boolean>(true)
  const [isCopying, setIsCopying] = useState<boolean>(false)
  const { installMarketplaceAgent } = useMarketplace()

  const handleCopy = async () => {
    try {
      setIsCopying(true)
      
      // Call the enhanced installation endpoint with customization options
      const result = await installMarketplaceAgent(listingId, {
        custom_agent_name: customName,
        preserve_original_reference: preserveReference
      })
      
      toast({
        title: 'Success',
        description: 'Agent copied successfully!',
        variant: 'success'
      })
      
      onCopySuccess(result.agent_id)
      
    } catch (error) {
      console.error('Failed to copy agent:', error)
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to copy agent',
        variant: 'destructive'
      })
    } finally {
      setIsCopying(false)
    }
  }

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomName(e.target.value)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Copy Marketplace Agent</DialogTitle>
          <DialogDescription>
            Customize the copy of "{listingTitle}" before adding it to your agents.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="agent-name" className="text-right">
              Agent Name
            </Label>
            <Input 
              id="agent-name" 
              value={customName}
              onChange={handleNameChange}
              className="col-span-3"
              placeholder="Enter agent name"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox 
              id="preserve-reference" 
              checked={preserveReference}
              onCheckedChange={(checked) => setPreserveReference(checked as boolean)}
            />
            <Label htmlFor="preserve-reference" className="text-sm font-medium leading-none">
              Preserve original agent reference
            </Label>
          </div>

          <div className="col-span-4 text-sm text-muted-foreground">
            <p className="mb-2">You are copying the agent:</p>
            <div className="bg-muted p-3 rounded-md">
              <p className="font-medium">{originalAgentName}</p>
              <p className="text-xs mt-1">Original agent will be referenced for attribution</p>
            </div>
          </div>

          <div className="col-span-4 text-sm">
            <h4 className="font-medium mb-2">What will be copied:</h4>
            <ul className="space-y-1 text-muted-foreground">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Agent configuration and settings</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Knowledge files and integrations</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Sub-agent configurations</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>Communication channels and hooks</span>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <span>All agent metadata and tags</span>
              </li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={onClose} 
            disabled={isCopying}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleCopy} 
            disabled={isCopying || !customName.trim()}
            className="bg-primary hover:bg-primary/90"
          >
            {isCopying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Copying...
              </>
            ) : (
              'Copy Agent'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}