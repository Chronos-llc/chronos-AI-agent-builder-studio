import { useState, useEffect } from 'react'
import { Card } from '../../ui/card'
import { Button } from '../../ui/button'
import { Input } from '../../ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../ui/select'
import { Badge } from '../../ui/badge'
import { Switch } from '../../ui/switch'
import { Alert, AlertDescription } from '../../ui/alert'
import { 
  Search, 
  Filter, 
  PlusCircle, 
  Edit, 
  Trash2, 
  RefreshCw, 
  AlertCircle,
  Loader2,
  CheckCircle2,
  XCircle,
  Tag
} from 'lucide-react'
import { 
  getSkills, 
  deleteSkill, 
  getSkillCategories,
  discoverSkills
} from '../../../services/skillsService'
import type { Skill } from '../../../types/skills'

interface SkillsLibraryProps {
  onEditSkill?: (skillId: number) => void
}

const ALL_CATEGORIES_VALUE = '__all__'

export const SkillsLibrary = ({ onEditSkill }: SkillsLibraryProps) => {
  const [skills, setSkills] = useState<Skill[]>([])
  const [categories, setCategories] = useState<{ name: string; count: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [discovering, setDiscovering] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showInactive, setShowInactive] = useState(false)
  const [showPremiumOnly, setShowPremiumOnly] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const [totalSkills, setTotalSkills] = useState(0)

  useEffect(() => {
    loadSkills()
    loadCategories()
  }, [currentPage, searchQuery, selectedCategory, showInactive, showPremiumOnly])

  const loadSkills = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params: Record<string, any> = {
        page: currentPage,
        page_size: pageSize,
        sort_by: 'name',
        sort_order: 'asc'
      }
      
      if (searchQuery) params.search_query = searchQuery
      if (selectedCategory) params.category = selectedCategory
      params.is_active = showInactive ? undefined : true
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

  const handleDiscoverSkills = async () => {
    try {
      setDiscovering(true)
      setError(null)
      
      const result = await discoverSkills()
      
      // Refresh skills list after discovery
      await loadSkills()
      await loadCategories()
      
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discover skills')
      console.error('Error discovering skills:', err)
      throw err
    } finally {
      setDiscovering(false)
    }
  }

  const handleDeleteSkill = async (skillId: number) => {
    if (!window.confirm('Are you sure you want to delete this skill? This action cannot be undone.')) {
      return
    }
    
    try {
      await deleteSkill(skillId)
      // Refresh skills list
      await loadSkills()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete skill')
      console.error('Error deleting skill:', err)
    }
  }

  const handleToggleActive = async (skill: Skill) => {
    // This would be implemented with an update API call
    console.log('Toggle active status for skill:', skill.id)
    // In a real implementation:
    // await updateSkill(skill.id, { is_active: !skill.is_active })
    // await loadSkills()
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
      {/* Header with Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">Skills Library</h2>
          <Badge variant="secondary">{totalSkills} skills</Badge>
        </div>
        
        <div className="flex items-center gap-2 flex-wrap">
          <Button 
            onClick={handleDiscoverSkills}
            disabled={discovering}
            className="gap-2"
          >
            {discovering ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            {discovering ? 'Discovering...' : 'Discover Skills'}
          </Button>
          
          <Button variant="outline" className="gap-2">
            <PlusCircle className="w-4 h-4" />
            Create Skill
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 items-end">
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
                id="show-inactive"
                checked={showInactive}
                onCheckedChange={(checked) => {
                  setShowInactive(checked)
                  setCurrentPage(1)
                }}
              />
              <label htmlFor="show-inactive" className="text-sm font-medium">
                Show Inactive
              </label>
            </div>
            
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
          
          <div className="flex justify-end">
            <Button 
              variant="outline"
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory(null)
                setShowInactive(false)
                setShowPremiumOnly(false)
                setCurrentPage(1)
              }}
              className="gap-2"
            >
              <XCircle className="w-4 h-4" />
              Reset Filters
            </Button>
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {skills.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-muted-foreground mb-4">No skills found</p>
              <Button 
                variant="outline"
                onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory(null)
                  setShowInactive(false)
                  setShowPremiumOnly(false)
                }}
              >
                Reset Filters
              </Button>
            </div>
          ) : (
            skills.map((skill) => (
              <Card key={skill.id} className="p-4 hover:shadow-lg transition-shadow">
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
                      <Badge variant={skill.is_active ? 'default' : 'secondary'}>
                        {skill.is_active ? 'Active' : 'Inactive'}
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
                  
                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-2 border-t">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1 gap-1"
                      onClick={() => onEditSkill?.(skill.id)}
                    >
                      <Edit className="w-3 h-3" />
                      Edit
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1 gap-1"
                      onClick={() => handleToggleActive(skill)}
                    >
                      {skill.is_active ? (
                        <XCircle className="w-3 h-3 text-red-500" />
                      ) : (
                        <CheckCircle2 className="w-3 h-3 text-green-500" />
                      )}
                      {skill.is_active ? 'Disable' : 'Enable'}
                    </Button>
                    <Button 
                      variant="destructive" 
                      size="sm" 
                      className="flex-1 gap-1"
                      onClick={() => handleDeleteSkill(skill.id)}
                    >
                      <Trash2 className="w-3 h-3" />
                      Delete
                    </Button>
                  </div>
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
