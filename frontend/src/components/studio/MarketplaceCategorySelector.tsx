import { useState } from 'react';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/select';
import { Check, ChevronsUpDown } from 'lucide-react';
import type { MarketplaceCategory } from '../../types/marketplace';

interface MarketplaceCategorySelectorProps {
    categories: MarketplaceCategory[];
    selectedCategoryId?: number;
    onSelect: (categoryId?: number) => void;
}

export const MarketplaceCategorySelector = ({
    categories,
    selectedCategoryId,
    onSelect
}: MarketplaceCategorySelectorProps) => {
    const [isOpen, setIsOpen] = useState(false);

    const handleSelect = (categoryId: string) => {
        const id = categoryId === 'none' ? undefined : parseInt(categoryId);
        onSelect(id);
        setIsOpen(false);
    };

    const selectedCategory = categories.find(cat => cat.id === selectedCategoryId);

    return (
        <Select 
            open={isOpen} 
            onOpenChange={setIsOpen} 
            value={selectedCategoryId?.toString() || 'none'}
            onValueChange={handleSelect}
        >
            <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a category">
                    {selectedCategory ? selectedCategory.display_name : 'Select a category'}
                </SelectValue>
                <ChevronsUpDown className="w-4 h-4 opacity-50" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="none">
                    <div className="flex items-center">
                        <span>None</span>
                    </div>
                </SelectItem>
                {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id.toString()}>
                        <div className="flex items-center">
                            {selectedCategoryId === category.id && (
                                <Check className="w-4 h-4 mr-2 text-primary" />
                            )}
                            <span>{category.display_name}</span>
                        </div>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    );
};