import { useState, useEffect } from 'react'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Badge } from '../ui/badge'
import { Switch } from '../ui/switch'
import { Alert, AlertDescription } from '../ui/alert'
import { 
  Search, 
  Filter, 
  PlusCircle, 
  CheckCircle2,
  AlertCircle,
  Loader2,
  Tag,
  XCircle
} from 'lucide-react'
import { getSkills, getSkillCategories } from '../../services/skillsService'
import type { Skill } from '../../types/skills'

const ALL_CATEGORIES_VALUE = '__all__'

export const SkillSelector = ({ onSkillsAdded }: { onSkillsAdded?: () => void }) => {
  const [skills, setSkills] = useState<Skill[]>([])
  const [categories, setCategories] = useState<{ name: string; count: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showPremiumOnly, setShowPremiumOnly] = useState(false)
  const [selectedSkills, setSelectedSkills] = useState<Set<number>>(new Set())
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(12)
  const [totalSkills, setTotalSkills] = useState(0)

  useEffect(() => {
    loadSkills()
    loadCategories()
  }, [currentPage, searchQuery, selectedCategory, showPremiumOnly])

  const loadSkills = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params: Record<string, any> = {
        page: currentPage,
        page_size: pageSize,
        sort_by: 'install_count',
        sort_order: 'desc',
        is_active: true
      }
      
      if (searchQuery) params.search_query = searchQuery
      if (selectedCategory) params.category = selectedCategory
      if (showPremiumOnly) params.is_premium = true
      
      const result = await getSkills(
        params.category,
        undefined,
        params.is_active,
        params.is_premium,
        params.search_query,
        params.sort_by,
        params.sort_order,
        params.page,
        params.page_size
      )
      
      setSkills(result.items)
      setTotalSkills(result.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load skills')
      console.error('Error loading skills:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const result = await getSkillCategories()
      setCategories(result.categories)
    } catch (err) {
      console.error('Error loading categories:', err)
    }
  }

  const handleToggleSkill = (skillId: number) => {
    setSelectedSkills(prev => {
      const newSet = new Set(prev)
      if (newSet.has(skillId)) {
        newSet.delete(skillId)
      } else {
        newSet.add(skillId)
      }
      return newSet
    })
  }

  const handleAddSelectedSkills = () => {
    const selectedSkillIds = Array.from(selectedSkills)
    if (selectedSkillIds.length === 0) {
      setError('Please select at least one skill')
      return
    }
    
    // This would be handled by the parent component
    console.log('Adding skills:', selectedSkillIds)
    // In a real implementation, this would call a prop like onSkillsSelected(selectedSkillIds)
    onSkillsAdded?.()
  }

  const getCategoryIcon = (category?: string) => {
    if (!category) return '📚'
    
    const icons: Record<string, string> = {
      'analysis': '📊',
      'automation': '⚙️',
      'communication': '💬',
      'integration': '🔗',
      'data': '🗃️',
      'ai': '🤖',
      'utility': '🔧'
    }
    
    return icons[category.toLowerCase()] || '📚'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Skills Library</h2>
          <p className="text-muted-foreground mt-1">
            Browse and add skills to your agent
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            onClick={handleAddSelectedSkills}
            disabled={selectedSkills.size === 0}
            className="gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            Add Selected ({selectedSkills.size})
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div className="space-y-2">
            <label htmlFor="search" className="text-sm font-medium flex items-center gap-1">
              <Search className="w-4 h-4" />
              Search Skills
            </label>
            <Input
              id="search"
              placeholder="Search by name, description..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setCurrentPage(1)
              }}
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="category" className="text-sm font-medium flex items-center gap-1">
              <Filter className="w-4 h-4" />
              Category
            </label>
            <Select 
              value={selectedCategory || ALL_CATEGORIES_VALUE}
              onValueChange={(value) => {
                setSelectedCategory(value === ALL_CATEGORIES_VALUE ? null : value)
                setCurrentPage(1)
              }}
            >
              <SelectTrigger id="category">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL_CATEGORIES_VALUE}>All Categories</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.name} value={category.name}>
                    {category.name} ({category.count})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Switch 
                id="show-premium"
                checked={showPremiumOnly}
                onCheckedChange={(checked) => {
                  setShowPremiumOnly(checked)
                  setCurrentPage(1)
                }}
              />
              <label htmlFor="show-premium" className="text-sm font-medium">
                Premium Only
              </label>
            </div>
          </div>
        </div>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Skills Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {skills.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-muted-foreground mb-4">No skills found</p>
              <Button 
                variant="outline"
                onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory(null)
                  setShowPremiumOnly(false)
                }}
              >
                Reset Filters
              </Button>
            </div>
          ) : (
            skills.map((skill) => (
              <Card 
                key={skill.id} 
                className={`p-4 hover:shadow-lg transition-shadow cursor-pointer ${
                  selectedSkills.has(skill.id) ? 'border-primary border-2' : ''
                }`}
                onClick={() => handleToggleSkill(skill.id)}
              >
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary text-primary-foreground rounded-lg flex items-center justify-center font-bold text-lg">
                        {getCategoryIcon(skill.category)}
                      </div>
                      <div>
                        <h3 className="font-semibold">{skill.display_name}</h3>
                        <p className="text-sm text-muted-foreground">{skill.name}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {skill.is_premium && (
                        <Badge variant="secondary" className="gap-1">
                          <Tag className="w-3 h-3" />
                          Premium
                        </Badge>
                      )}
                      <Badge variant="default" className="gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Active
                      </Badge>
                    </div>
                  </div>
                  
                  {/* Description */}
                  <div className="text-sm text-muted-foreground">
                    <p className="line-clamp-3">{skill.description || 'No description provided'}</p>
                  </div>
                  
                  {/* Metadata */}
                  <div className="flex flex-wrap gap-2 text-xs">
                    {skill.category && (
                      <Badge variant="outline" className="gap-1">
                        {skill.category}
                      </Badge>
                    )}
                    {skill.version && (
                      <Badge variant="outline" className="gap-1">
                        v{skill.version}
                      </Badge>
                    )}
                    <Badge variant="outline" className="gap-1">
                      {skill.install_count} installs
                    </Badge>
                  </div>
                  
                  {/* Selection Indicator */}
                  {selectedSkills.has(skill.id) && (
                    <div className="flex items-center justify-center pt-2 border-t">
                      <Badge variant="default" className="gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Selected
                      </Badge>
                    </div>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}
      
      {/* Pagination */}
      {totalSkills > pageSize && (
        <div className="flex items-center justify-center gap-4 pt-6">
          <Button 
            variant="outline"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {currentPage} of {Math.ceil(totalSkills / pageSize)}
          </span>
          <Button 
            variant="outline"
            disabled={currentPage * pageSize >= totalSkills}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
