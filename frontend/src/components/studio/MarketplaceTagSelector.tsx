import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Check, ChevronsUpDown, X } from 'lucide-react';
import type { MarketplaceTag } from '@/types/marketplace';

interface MarketplaceTagSelectorProps {
  tags: MarketplaceTag[];
  selectedTags: string[];
  onSelect: (selectedTags: string[]) => void;
}

export const MarketplaceTagSelector = ({ 
  tags, 
  selectedTags, 
  onSelect 
}: MarketplaceTagSelectorProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleTagToggle = (tagName: string) => {
    const newSelectedTags = selectedTags.includes(tagName)
      ? selectedTags.filter(t => t !== tagName)
      : [...selectedTags, tagName];
    onSelect(newSelectedTags);
  };

  const filteredTags = tags.filter(tag =>
    tag.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tag.display_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}> 
      <PopoverTrigger asChild>
        <Button 
          variant="outline" 
          role="combobox" 
          aria-expanded={isOpen} 
          className="w-full justify-between"
        >
          {selectedTags.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {selectedTags.slice(0, 3).map((tag, index) => (
                <Badge key={index} variant="secondary" className="gap-1">
                  <span>{tag}</span>
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="icon" 
                    className="w-3 h-3 rounded-full" 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTagToggle(tag);
                    }}
                  >
                    <X className="w-2 h-2" />
                  </Button>
                </Badge>
              ))}
              {selectedTags.length > 3 && (
                <Badge variant="secondary">+{selectedTags.length - 3} more</Badge>
              )}
            </div>
          ) : (
            <span>Select tags...</span>
          )}
          <ChevronsUpDown className="w-4 h-4 ml-2 opacity-50 shrink-0" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <div className="p-2">
          <Input 
            placeholder="Search tags..." 
            value={searchTerm} 
            onChange={(e) => setSearchTerm(e.target.value)} 
            className="mb-2"
          />
          <div className="max-h-60 overflow-y-auto">
            {filteredTags.length > 0 ? (
              <div className="space-y-1">
                {filteredTags.map((tag) => (
                  <div 
                    key={tag.id} 
                    className={`flex items-center space-x-2 p-2 rounded cursor-pointer hover:bg-accent ${
                      selectedTags.includes(tag.name) ? 'bg-primary text-primary-foreground' : ''
                    }`} 
                    onClick={() => handleTagToggle(tag.name)}
                  >
                    <Check 
                      className={`w-4 h-4 ${
                        selectedTags.includes(tag.name) ? 'opacity-100' : 'opacity-0'
                      }`}
                    />
                    <span>{tag.display_name}</span>
                    <Badge variant="secondary" className="ml-auto">
                      {tag.usage_count}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-sm text-muted-foreground">
                No tags found
              </div>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};