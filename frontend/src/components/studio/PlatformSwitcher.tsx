import React from 'react'
import { Tabs, TabsList, TabsTrigger } from '../ui/tabs'
import { MessageSquare, Mic } from 'lucide-react'

interface PlatformSwitcherProps {
  value: 'text' | 'voice'
  onChange: (value: 'text' | 'voice') => void
  className?: string
}

export const PlatformSwitcher: React.FC<PlatformSwitcherProps> = ({
  value,
  onChange,
  className
}) => {
  const handleValueChange = (newValue: string) => {
    if (newValue === 'text' || newValue === 'voice') {
      onChange(newValue)
    }
  }

  return (
    <Tabs value={value} onValueChange={handleValueChange} className={className}>
      <TabsList className="bg-card/60 border border-border p-1">
        <TabsTrigger
          value="text"
          className="flex items-center gap-2 px-4 py-2 rounded-md data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Text Agents</span>
        </TabsTrigger>
        <TabsTrigger
          value="voice"
          className="flex items-center gap-2 px-4 py-2 rounded-md data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
        >
          <Mic className="w-4 h-4" />
          <span>Voice Agents</span>
        </TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
