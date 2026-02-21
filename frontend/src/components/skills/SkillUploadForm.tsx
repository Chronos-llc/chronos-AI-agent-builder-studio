import { useState, type FormEvent } from 'react'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Textarea } from '../ui/textarea'
import { Checkbox } from '../ui/checkbox'
import type { SkillUploadResponse } from '../../types/skillMarketplace'

interface SkillUploadFormProps {
  onSubmit: (form: FormData) => Promise<SkillUploadResponse>
  submitLabel?: string
}

export function SkillUploadForm({ onSubmit, submitLabel = 'Upload Skill' }: SkillUploadFormProps) {
  const [file, setFile] = useState<File | null>(null)
  const [displayName, setDisplayName] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('')
  const [version, setVersion] = useState('1.0.0')
  const [visibility, setVisibility] = useState<'public' | 'private'>('public')
  const [premium, setPremium] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SkillUploadResponse | null>(null)

  const handleFormSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setResult(null)

    if (!file) {
      setError('Please upload a SKILL.md file.')
      return
    }
    if (!file.name.toLowerCase().endsWith('.md')) {
      setError('Only markdown skill files are allowed.')
      return
    }

    const form = new FormData()
    form.append('skill_file', file)
    if (displayName.trim()) form.append('display_name', displayName.trim())
    if (description.trim()) form.append('description', description.trim())
    if (category.trim()) form.append('category', category.trim())
    if (version.trim()) form.append('version', version.trim())
    form.append('visibility', visibility)
    form.append('is_premium', String(premium))

    try {
      setSubmitting(true)
      const uploadResult = await onSubmit(form)
      setResult(uploadResult)
      setFile(null)
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Upload failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card className="border border-border bg-card p-4 text-card-foreground" data-testid="skill-upload-form-card">
      <form className="space-y-4" onSubmit={handleFormSubmit} data-testid="skill-upload-form">
        <div className="space-y-2">
          <Label htmlFor="skill-file" className="text-foreground">SKILL.md File</Label>
          <Input
            id="skill-file"
            type="file"
            data-testid="skill-upload-file-input"
            className="text-foreground file:mr-3 file:text-foreground"
            accept=".md,text/markdown"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="skill-display-name" className="text-foreground">Display name</Label>
            <Input id="skill-display-name" className="text-foreground placeholder:text-muted-foreground" data-testid="skill-upload-display-name-input" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="skill-version" className="text-foreground">Version</Label>
            <Input id="skill-version" className="text-foreground placeholder:text-muted-foreground" data-testid="skill-upload-version-input" value={version} onChange={(event) => setVersion(event.target.value)} />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="skill-category" className="text-foreground">Category</Label>
          <Input id="skill-category" className="text-foreground placeholder:text-muted-foreground" data-testid="skill-upload-category-input" value={category} onChange={(event) => setCategory(event.target.value)} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="skill-description" className="text-foreground">Description</Label>
          <Textarea
            id="skill-description"
            className="text-foreground placeholder:text-muted-foreground"
            data-testid="skill-upload-description-input"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            rows={3}
          />
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm text-foreground">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={visibility === 'public'}
              onChange={() => setVisibility('public')}
            />
            Public
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={visibility === 'private'}
              onChange={() => setVisibility('private')}
            />
            Private
          </label>
          <label className="flex items-center gap-2">
            <Checkbox checked={premium} onCheckedChange={(value) => setPremium(Boolean(value))} />
            Premium skill
          </label>
        </div>

        {error && <p className="text-sm text-red-600 dark:text-red-300" data-testid="skill-upload-error">{error}</p>}
        {result && (
          <p className="text-sm text-emerald-700 dark:text-emerald-300" data-testid="skill-upload-success">
            Uploaded. Status: {result.submission_status}. Scan: {result.scan_status}.
          </p>
        )}

        <Button type="submit" disabled={submitting} className="w-full bg-primary text-primary-foreground hover:bg-primary/90" data-testid="skill-upload-submit">
          {submitting ? 'Uploading...' : submitLabel}
        </Button>
      </form>
    </Card>
  )
}
