import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/select';
import { Label } from '../ui/label';
import { Checkbox } from '../ui/checkbox';
import { AlertTriangle, Info, Upload, X } from 'lucide-react';
import MarketplaceCategorySelector from './MarketplaceCategorySelector';
import MarketplaceTagSelector from './MarketplaceTagSelector';
import type { MarketplaceCategory, MarketplaceTag, MarketplaceListingCreate } from '../../types/marketplace';

interface MarketplacePublishingFormProps {
  agentId: number;
  agentName: string;
  categories: MarketplaceCategory[];
  tags: MarketplaceTag[];
  onSubmit: (formData: MarketplaceListingCreate) => void;
}

export const MarketplacePublishingForm = ({ 
  agentId, 
  agentName, 
  categories, 
  tags, 
  onSubmit 
}: MarketplacePublishingFormProps) => {
  const [formData, setFormData] = useState<MarketplaceListingCreate>({
    agent_id: agentId,
    title: agentName,
    description: '',
    category_id: undefined,
    tags: [],
    listing_type: 'AGENT',
    visibility: 'PUBLIC',
    version: '1.0.0',
    preview_images: [],
    demo_video_url: '',
    schema_data: {}
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isValid, setIsValid] = useState(false);
  const [fileUploads, setFileUploads] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    validateForm();
  }, [formData]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (!formData.category_id) {
      newErrors.category_id = 'Category is required';
    }
    
    if (formData.tags && formData.tags.length === 0) {
      newErrors.tags = 'At least one tag is required';
    }
    
    setErrors(newErrors);
    setIsValid(Object.keys(newErrors).length === 0);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCategorySelect = (categoryId?: number) => {
    setFormData(prev => ({ ...prev, category_id: categoryId }));
  };

  const handleTagSelect = (selectedTags: string[]) => {
    setFormData(prev => ({ ...prev, tags: selectedTags }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setFileUploads(prev => [...prev, ...files]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setFileUploads(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isValid) {
      validateForm();
      return;
    }
    
    // In a real implementation, we would upload files first
    // For now, we'll just submit the form data
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-muted-foreground">Basic Information</h4>
        
        <div className="space-y-2">
          <Label htmlFor="title">Listing Title</Label>
          <Input 
            id="title" 
            name="title" 
            value={formData.title} 
            onChange={handleInputChange} 
            placeholder="Enter a descriptive title for your agent"
          />
          {errors.title && (
            <div className="flex items-center space-x-1 text-sm text-destructive">
              <AlertTriangle className="w-3 h-3" />
              <span>{errors.title}</span>
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea 
            id="description" 
            name="description" 
            value={formData.description} 
            onChange={handleInputChange} 
            placeholder="Describe your agent's capabilities, use cases, and features"
            rows={5}
          />
          {errors.description && (
            <div className="flex items-center space-x-1 text-sm text-destructive">
              <AlertTriangle className="w-3 h-3" />
              <span>{errors.description}</span>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="listing_type">Listing Type</Label>
            <Select 
              name="listing_type" 
              value={formData.listing_type} 
              onValueChange={(value) => handleSelectChange('listing_type', value as 'AGENT' | 'SUBAGENT')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select listing type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="AGENT">Agent</SelectItem>
                <SelectItem value="SUBAGENT">Sub-Agent</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="visibility">Visibility</Label>
            <Select 
              name="visibility" 
              value={formData.visibility} 
              onValueChange={(value) => handleSelectChange('visibility', value as 'PUBLIC' | 'PRIVATE' | 'UNLISTED')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select visibility" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PUBLIC">Public</SelectItem>
                <SelectItem value="PRIVATE">Private</SelectItem>
                <SelectItem value="UNLISTED">Unlisted</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="version">Version</Label>
          <Input 
            id="version" 
            name="version" 
            value={formData.version} 
            onChange={handleInputChange} 
            placeholder="e.g., 1.0.0"
          />
        </div>
      </div>
      
      {/* Category and Tags */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-muted-foreground">Classification</h4>
        
        <div className="space-y-2">
          <Label>Category</Label>
          <MarketplaceCategorySelector 
            categories={categories} 
            selectedCategoryId={formData.category_id} 
            onSelect={handleCategorySelect}
          />
          {errors.category_id && (
            <div className="flex items-center space-x-1 text-sm text-destructive">
              <AlertTriangle className="w-3 h-3" />
              <span>{errors.category_id}</span>
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <Label>Tags</Label>
          <MarketplaceTagSelector 
            tags={tags} 
            selectedTags={formData.tags || []} 
            onSelect={handleTagSelect}
          />
          {errors.tags && (
            <div className="flex items-center space-x-1 text-sm text-destructive">
              <AlertTriangle className="w-3 h-3" />
              <span>{errors.tags}</span>
            </div>
          )}
        </div>
      </div>
      
      {/* Media Uploads */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-muted-foreground">Media</h4>
        
        <div className="space-y-2">
          <Label>Preview Images</Label>
          <div className="flex items-center space-x-2">
            <Input 
              type="file" 
              accept="image/*" 
              multiple 
              onChange={handleFileChange} 
              className="cursor-pointer"
            />
            <Button type="button" variant="outline" size="sm">
              <Upload className="w-4 h-4 mr-2" />
              Upload Images
            </Button>
          </div>
          
          {fileUploads.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-2">
              {fileUploads.map((file, index) => (
                <div key={index} className="relative">
                  <div className="w-20 h-20 bg-gray-100 rounded border flex items-center justify-center overflow-hidden">
                    <img 
                      src={URL.createObjectURL(file)} 
                      alt={file.name} 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <Button 
                    type="button" 
                    variant="destructive" 
                    size="icon" 
                    className="absolute -top-2 -right-2 w-5 h-5" 
                    onClick={() => handleRemoveFile(index)}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="demo_video_url">Demo Video URL</Label>
          <Input 
            id="demo_video_url" 
            name="demo_video_url" 
            value={formData.demo_video_url || ''} 
            onChange={handleInputChange} 
            placeholder="https://youtube.com/... or https://vimeo.com/..."
          />
        </div>
      </div>
      
      {/* Pricing and License */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-muted-foreground">Pricing & License</h4>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Pricing Model</Label>
            <div className="flex space-x-4">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="pricing-free" 
                  checked={!formData.schema_data?.price} 
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setFormData(prev => ({
                        ...prev,
                        schema_data: { ...prev.schema_data, price: undefined }
                      }));
                    }
                  }}
                />
                <Label htmlFor="pricing-free" className="cursor-pointer">Free</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="pricing-paid" 
                  checked={!!formData.schema_data?.price} 
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setFormData(prev => ({
                        ...prev,
                        schema_data: { ...prev.schema_data, price: 9.99 }
                      }));
                    } else {
                      setFormData(prev => ({
                        ...prev,
                        schema_data: { ...prev.schema_data, price: undefined }
                      }));
                    }
                  }}
                />
                <Label htmlFor="pricing-paid" className="cursor-pointer">Paid</Label>
              </div>
            </div>
          </div>
          
          {formData.schema_data?.price !== undefined && (
            <div className="space-y-2">
              <Label htmlFor="price">Price (USD)</Label>
              <Input 
                id="price" 
                type="number" 
                min="0" 
                step="0.01" 
                value={formData.schema_data.price || ''} 
                onChange={(e) => {
                  const price = parseFloat(e.target.value);
                  setFormData(prev => ({
                    ...prev,
                    schema_data: { ...prev.schema_data, price }
                  }));
                }}
              />
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="license">License Type</Label>
          <Select 
            name="license" 
            value={formData.schema_data?.license || 'MIT'} 
            onValueChange={(value) => {
              setFormData(prev => ({
                ...prev,
                schema_data: { ...prev.schema_data, license: value }
              }));
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select license type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="MIT">MIT License</SelectItem>
              <SelectItem value="Apache-2.0">Apache 2.0</SelectItem>
              <SelectItem value="GPL-3.0">GPL 3.0</SelectItem>
              <SelectItem value="Proprietary">Proprietary</SelectItem>
              <SelectItem value="Other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* Support Information */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-muted-foreground">Support Information</h4>
        
        <div className="space-y-2">
          <Label htmlFor="support">Support Details</Label>
          <Textarea 
            id="support" 
            name="support" 
            value={formData.schema_data?.support || ''} 
            onChange={(e) => {
              setFormData(prev => ({
                ...prev,
                schema_data: { ...prev.schema_data, support: e.target.value }
              }));
            }}
            placeholder="Provide support contact information, documentation links, or other support details"
            rows={3}
          />
        </div>
      </div>
      
      {/* Submit Button */}
      <div className="flex justify-end">
        <Button type="submit" disabled={!isValid || isUploading}>
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            'Submit Listing'
          )}
        </Button>
      </div>
    </form>
  );
};