import { useState, useEffect } from 'react'
import { Card } from '../../ui/card'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Textarea } from '../../ui/textarea'
import { Label } from '../../ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select'
import { Switch } from '../../ui/switch'
import { Badge } from '../../ui/badge'
import { Alert, AlertDescription } from '../../ui/alert'
import { 
  Save, 
  Upload, 
  Plus, 
  X, 
  Tag, 
  AlertCircle,
  Loader2,
  CheckCircle2
} from 'lucide-react'
import { createSkill, updateSkill } from '../../../services/skillsService'
import type { Skill, SkillCreate, SkillUpdate } from '../../../types/skills'

export const SkillCreator = () => {
  const [skill, setSkill] = useState<Partial<Skill>>({
    name: '',
    display_name: '',
    description: '',
    category: 'analysis',
    icon: 'Code',
    version: '1.0.0',
    parameters: {},
    tags: [],
    file_path: '',
    content_preview: '',
    is_active: true,
    is_premium: false
  })
  
  const [newTag, setNewTag] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null)

  // Categories for selection
  const categories = [
    { value: 'analysis', label: 'Analysis' },
    { value: 'automation', label: 'Automation' },
    { value: 'communication', label: 'Communication' },
    { value: 'integration', label: 'Integration' },
    { value: 'data', label: 'Data Processing' },
    { value: 'ai', label: 'AI/ML' },
    { value: 'utility', label: 'Utility' }
  ]

  // Common icons for selection
  const icons = [
    'Code', 'ChartBar', 'CalendarClock', 'Mail', 'Link', 'Database', 'Cpu', 'Brain', 'Tool', 'Puzzle'
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setSkill(prev => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setSkill(prev => ({ ...prev, [name]: value }))
  }

  const handleSwitchChange = (name: string, checked: boolean) => {
    setSkill(prev => ({ ...prev, [name]: checked }))
  }

  const handleAddTag = () => {
    if (newTag.trim() && !skill.tags?.includes(newTag.trim())) {
      setSkill(prev => ({ 
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }))
      setNewTag('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setSkill(prev => ({ 
      ...prev,
      tags: (prev.tags || []).filter(tag => tag !== tagToRemove)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      setIsSubmitting(true)
      setError(null)
      setSuccess(null)
      
      // Validate required fields
      if (!skill.name?.trim()) {
        throw new Error('Skill name is required')
      }
      
      if (!skill.display_name?.trim()) {
        throw new Error('Display name is required')
      }
      
      if (!skill.file_path?.trim()) {
        throw new Error('File path is required')
      }
      
      const skillData: SkillCreate | SkillUpdate = {
        name: skill.name,
        display_name: skill.display_name,
        description: skill.description || undefined,
        category: skill.category || undefined,
        icon: skill.icon || undefined,
        version: skill.version || undefined,
        parameters: skill.parameters || undefined,
        tags: skill.tags || undefined,
        file_path: skill.file_path,
        content_preview: skill.content_preview || undefined,
        is_active: skill.is_active,
        is_premium: skill.is_premium
      }
      
      if (editingId) {
        // Update existing skill
        await updateSkill(editingId, skillData as SkillUpdate)
        setSuccess('Skill updated successfully!')
      } else {
        // Create new skill
        await createSkill(skillData as SkillCreate)
        setSuccess('Skill created successfully!')
        
        // Reset form after creation
        setSkill({
          name: '',
          display_name: '',
          description: '',
          category: 'analysis',
          icon: 'Code',
          version: '1.0.0',
          parameters: {},
          tags: [],
          file_path: '',
          content_preview: '',
          is_active: true,
          is_premium: false
        })
      }
      
      // Scroll to top to show success message
      window.scrollTo({ top: 0, behavior: 'smooth' })
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save skill')
      console.error('Error saving skill:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // In a real implementation, this would upload the file and get a URL
      // For now, we'll just use the file name
      setSkill(prev => ({ 
        ...prev,
        file_path: `backend/skills/${skill.category || 'analysis'}/${file.name}`
      }))
      
      // Read file content for preview
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        setSkill(prev => ({ 
          ...prev,
          content_preview: content.substring(0, 500)
        }))
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Create New Skill</h2>
          <p className="text-muted-foreground mt-1">
            Define a new skill for AI agents to use
          </p>
        </div>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {success && (
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Skill Creation Form */}
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="name">Skill Name *</Label>
              <Input 
                id="name"
                name="name"
                value={skill.name}
                onChange={handleInputChange}
                placeholder="e.g., data_analyzer"
                required
              />
              <p className="text-xs text-muted-foreground">
                Unique identifier for the skill (used in code)
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="display_name">Display Name *</Label>
              <Input 
                id="display_name"
                name="display_name"
                value={skill.display_name}
                onChange={handleInputChange}
                placeholder="e.g., Data Analyzer"
                required
              />
              <p className="text-xs text-muted-foreground">
                User-friendly name for the skill
              </p>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea 
              id="description"
              name="description"
              value={skill.description}
              onChange={handleInputChange}
              placeholder="Describe what this skill does..."
              rows={4}
            />
            <p className="text-xs text-muted-foreground">
              Detailed description of the skill's functionality
            </p>
          </div>

          {/* Category and Icon */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select 
                value={skill.category || ''}
                onValueChange={(value) => handleSelectChange('category', value)}
              >
                <SelectTrigger id="category">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="icon">Icon</Label>
              <Select 
                value={skill.icon || ''}
                onValueChange={(value) => handleSelectChange('icon', value)}
              >
                <SelectTrigger id="icon">
                  <SelectValue placeholder="Select icon" />
                </SelectTrigger>
                <SelectContent>
                  {icons.map((icon) => (
                    <SelectItem key={icon} value={icon}>{icon}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Version and Parameters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="version">Version</Label>
              <Input 
                id="version"
                name="version"
                value={skill.version}
                onChange={handleInputChange}
                placeholder="e.g., 1.0.0"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Parameters (JSON)</Label>
              <Textarea 
                value={JSON.stringify(skill.parameters || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const parsed = JSON.parse(e.target.value)
                    setSkill(prev => ({ ...prev, parameters: parsed }))
                  } catch {
                    // Ignore JSON parse errors during typing
                  }
                }}
                placeholder="Define skill parameters as JSON..."
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                Define configurable parameters for the skill
              </p>
            </div>
          </div>

          {/* Tags */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Tags</Label>
              <p className="text-xs text-muted-foreground">
                Add tags for categorization and search
              </p>
            </div>
            
            <div className="flex gap-2">
              <Input 
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag..."
                onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
              />
              <Button type="button" onClick={handleAddTag} size="sm" className="gap-1">
                <Plus className="w-4 h-4" />
                Add
              </Button>
            </div>
            
            {skill.tags?.length ? (
              <div className="flex flex-wrap gap-2">
                {skill.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="gap-1">
                    <Tag className="w-3 h-3" />
                    {tag}
                    <button 
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No tags added yet</p>
            )}
          </div>

          {/* File Upload */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Skill File *</Label>
              <p className="text-xs text-muted-foreground">
                Upload the Python skill file
              </p>
            </div>
            
            <div className="border-2 border-dashed border-muted rounded-lg p-6 text-center">
              {skill.file_path ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                    <span className="font-medium">File Selected</span>
                  </div>
                  <p className="text-sm text-muted-foreground break-all">
                    {skill.file_path}
                  </p>
                  <Button 
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setSkill(prev => ({ ...prev, file_path: '', content_preview: '' }))}
                  >
                    Remove File
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-8 h-8 mx-auto text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Drag & drop skill file or click to browse
                  </p>
                  <input 
                    type="file"
                    accept=".py"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button 
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    Browse Files
                  </Button>
                </div>
              )}
            </div>
            
            {skill.content_preview && (
              <div className="space-y-2">
                <Label>File Preview</Label>
                <Textarea 
                  value={skill.content_preview}
                  readOnly
                  rows={6}
                  className="font-mono text-xs"
                />
              </div>
            )}
          </div>

          {/* Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <Label className="font-medium">Active</Label>
                <p className="text-sm text-muted-foreground">
                  Enable/disable this skill for users
                </p>
              </div>
              <Switch 
                checked={skill.is_active || false}
                onCheckedChange={(checked) => handleSwitchChange('is_active', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <Label className="font-medium">Premium</Label>
                <p className="text-sm text-muted-foreground">
                  Mark as premium skill
                </p>
              </div>
              <Switch 
                checked={skill.is_premium || false}
                onCheckedChange={(checked) => handleSwitchChange('is_premium', checked)}
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting} className="gap-2">
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {isSubmitting ? 'Saving...' : editingId ? 'Update Skill' : 'Create Skill'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}