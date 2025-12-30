import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Image, Video, Code, Trash2, Search, Filter, MoreVertical, Eye, Edit, Download, Plus, Folder, Database, X, Check, AlertTriangle, Info, HelpCircle } from 'lucide-react'

interface KnowledgeItem {
    id: string
    name: string
    type: 'text' | 'pdf' | 'image' | 'video' | 'code' | 'other'
    size: number
    content: string
    metadata: any
    created_at: string
    status?: 'processing' | 'ready' | 'error'
}

interface KnowledgeBaseProps {
    items: KnowledgeItem[]
    onItemsChange: (items: KnowledgeItem[]) => void
    onFileUpload: (files: File[]) => void
}

export const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({
    items: initialItems,
    onItemsChange,
    onFileUpload
}) => {
    const [items, setItems] = useState<KnowledgeItem[]>(initialItems)
    const [searchQuery, setSearchQuery] = useState('')
    const [filterType, setFilterType] = useState<'all' | 'text' | 'pdf' | 'image' | 'video' | 'code'>('all')
    const [showUploadDialog, setShowUploadDialog] = useState(false)
    const [processingFiles, setProcessingFiles] = useState<File[]>([])
    const [uploadProgress, setUploadProgress] = useState<number[]>([])

    // Update items when props change
    React.useEffect(() => {
        setItems(initialItems)
    }, [initialItems])

    // Handle file drop
    const onDrop = useCallback((acceptedFiles: File[]) => {
        setShowUploadDialog(false)
        setProcessingFiles(acceptedFiles)
        setUploadProgress(new Array(acceptedFiles.length).fill(0))

        // Simulate file processing
        const newItems: KnowledgeItem[] = []
        acceptedFiles.forEach((file, index) => {
            const fileType = getFileType(file)

            // Simulate processing progress
            const interval = setInterval(() => {
                setUploadProgress(prev => {
                    const newProgress = [...prev]
                    newProgress[index] = Math.min(newProgress[index] + 10, 90)
                    return newProgress
                })
            }, 200)

            // Simulate completion
            setTimeout(() => {
                clearInterval(interval)
                setUploadProgress(prev => {
                    const newProgress = [...prev]
                    newProgress[index] = 100
                    return newProgress
                })

                newItems.push({
                    id: Date.now() + index + '',
                    name: file.name,
                    type: fileType,
                    size: file.size,
                    content: `Content extracted from ${file.name}`,
                    metadata: {
                        fileType: file.type,
                        lastModified: file.lastModified
                    },
                    created_at: new Date().toISOString(),
                    status: 'ready'
                })

                // Update state
                setItems(prev => [...prev, ...newItems])
                onItemsChange([...prev, ...newItems])

                // Clear processing state after all files are done
                if (index === acceptedFiles.length - 1) {
                    setTimeout(() => {
                        setProcessingFiles([])
                        setUploadProgress([])
                    }, 1000)
                }
            }, 2000 + index * 500)
        })

        // Call the upload handler
        onFileUpload(acceptedFiles)
    }, [onFileUpload, initialItems])

    const getFileType = (file: File): KnowledgeItem['type'] => {
        if (file.type.startsWith('image/')) return 'image'
        if (file.type.startsWith('video/')) return 'video'
        if (file.type === 'application/pdf') return 'pdf'
        if (file.type.startsWith('text/')) return 'text'
        if (file.name.endsWith('.js') || file.name.endsWith('.ts') ||
            file.name.endsWith('.py') || file.name.endsWith('.java') ||
            file.name.endsWith('.cpp') || file.name.endsWith('.html') ||
            file.name.endsWith('.css') || file.name.endsWith('.json')) return 'code'
        return 'other'
    }

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/*': ['.txt', '.md', '.json', '.csv'],
            'application/pdf': ['.pdf'],
            'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            'video/*': ['.mp4', '.webm', '.mov'],
            'application/javascript': ['.js'],
            'application/typescript': ['.ts'],
            'text/x-python': ['.py'],
            'text/x-java': ['.java'],
            'text/x-c': ['.c', '.cpp', '.h']
        },
        multiple: true
    })

    const filteredItems = items.filter(item => {
        const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.content.toLowerCase().includes(searchQuery.toLowerCase())
        const matchesFilter = filterType === 'all' || item.type === filterType
        return matchesSearch && matchesFilter
    })

    const handleRemoveItem = (id: string) => {
        const newItems = items.filter(item => item.id !== id)
        setItems(newItems)
        onItemsChange(newItems)
    }

    const handleRemoveAll = () => {
        setItems([])
        onItemsChange([])
    }

    const getFileIcon = (type: KnowledgeItem['type']) => {
        switch (type) {
            case 'text': return <FileText className="w-4 h-4 text-blue-500" />
            case 'pdf': return <FileText className="w-4 h-4 text-red-500" />
            case 'image': return <Image className="w-4 h-4 text-green-500" />
            case 'video': return <Video className="w-4 h-4 text-purple-500" />
            case 'code': return <Code className="w-4 h-4 text-yellow-500" />
            default: return <FileText className="w-4 h-4" />
        }
    }

    const getFileTypeLabel = (type: KnowledgeItem['type']) => {
        return type.charAt(0).toUpperCase() + type.slice(1)
    }

    return (
        <div className="knowledge-base">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    <span>Knowledge Base</span>
                </h2>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowUploadDialog(true)}
                        className="flex items-center gap-2 px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                    >
                        <Upload className="w-4 h-4" />
                        <span>Upload Files</span>
                    </button>
                    {items.length > 0 && (
                        <button
                            onClick={handleRemoveAll}
                            className="flex items-center gap-2 px-3 py-1 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90"
                        >
                            <Trash2 className="w-4 h-4" />
                            <span>Clear All</span>
                        </button>
                    )}
                </div>
            </div>

            {/* Search and Filter */}
            <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search knowledge base..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 border border-input rounded-md bg-background text-foreground"
                    />
                </div>

                <div className="relative">
                    <select
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value as any)}
                        className="pl-3 pr-8 py-2 border border-input rounded-md bg-background text-foreground appearance-none"
                    >
                        <option value="all">All Types</option>
                        <option value="text">Text</option>
                        <option value="pdf">PDF</option>
                        <option value="image">Images</option>
                        <option value="video">Videos</option>
                        <option value="code">Code</option>
                    </select>
                    <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                </div>
            </div>

            {/* File Processing Indicator */}
            {processingFiles.length > 0 && (
                <div className="mb-4 p-4 bg-secondary rounded-lg">
                    <h3 className="font-medium mb-3 flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Processing Files</span>
                    </h3>
                    <div className="space-y-2">
                        {processingFiles.map((file, index) => (
                            <div key={index} className="flex items-center gap-2">
                                <div className="w-4 h-4 flex items-center justify-center">
                                    {getFileIcon(getFileType(file))}
                                </div>
                                <span className="text-sm flex-1 truncate">{file.name}</span>
                                <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-primary"
                                        style={{ width: `${uploadProgress[index]}%` }}
                                    />
                                </div>
                                <span className="text-xs text-muted-foreground w-8 text-right">
                                    {uploadProgress[index]}%
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Knowledge Items */}
            {filteredItems.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-border rounded-lg">
                    <div className="flex flex-col items-center gap-4">
                        <Upload className="w-8 h-8 text-muted-foreground" />
                        <h3 className="font-medium">No knowledge items found</h3>
                        <p className="text-sm text-muted-foreground max-w-md">
                            Upload files to build your agent's knowledge base. Supported formats:
                            PDF, text, images, videos, and code files.
                        </p>
                        <button
                            onClick={() => setShowUploadDialog(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                        >
                            <Upload className="w-4 h-4" />
                            <span>Upload Files</span>
                        </button>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredItems.map(item => (
                        <div key={item.id} className="border border-border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                            <div className="p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <div className="w-6 h-6 flex items-center justify-center">
                                            {getFileIcon(item.type)}
                                        </div>
                                        <span className="font-medium truncate max-w-[150px]">{item.name}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        {item.status === 'processing' && (
                                            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                                        )}
                                        {item.status === 'error' && (
                                            <AlertTriangle className="w-4 h-4 text-destructive" />
                                        )}
                                        <button
                                            onClick={() => handleRemoveItem(item.id)}
                                            className="text-muted-foreground hover:text-destructive"
                                            title="Remove item"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>

                                <div className="text-sm text-muted-foreground mb-2">
                                    {getFileTypeLabel(item.type)} • {(item.size / 1024).toFixed(1)} KB
                                </div>

                                <div className="text-sm text-muted-foreground line-clamp-3 mb-3">
                                    {item.content}
                                </div>

                                <div className="flex gap-2">
                                    <button
                                        className="flex items-center gap-1 px-2 py-1 text-xs bg-secondary rounded-md hover:bg-secondary/80"
                                        title="Edit content"
                                    >
                                        <Edit className="w-3 h-3" />
                                        <span>Edit</span>
                                    </button>
                                    <button
                                        className="flex items-center gap-1 px-2 py-1 text-xs bg-secondary rounded-md hover:bg-secondary/80"
                                        title="Preview content"
                                    >
                                        <Eye className="w-3 h-3" />
                                        <span>Preview</span>
                                    </button>
                                    <button
                                        className="flex items-center gap-1 px-2 py-1 text-xs bg-secondary rounded-md hover:bg-secondary/80"
                                        title="Download file"
                                    >
                                        <Download className="w-3 h-3" />
                                        <span>Download</span>
                                    </button>
                                </div>

                                {item.metadata && Object.keys(item.metadata).length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-border">
                                        <div className="text-xs text-muted-foreground">
                                            <div className="font-medium mb-1">Metadata:</div>
                                            <div className="grid grid-cols-2 gap-1">
                                                {Object.entries(item.metadata).map(([key, value]) => (
                                                    <div key={key} className="flex justify-between">
                                                        <span className="text-muted-foreground">{key}:</span>
                                                        <span className="truncate max-w-[100px]">{String(value)}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {item.status === 'processing' && (
                                <div className="h-1 bg-primary/20">
                                    <div className="h-full bg-primary animate-pulse" style={{ width: '50%' }} />
                                </div>
                            )}
                            {item.status === 'error' && (
                                <div className="h-1 bg-destructive/20">
                                    <div className="h-full bg-destructive" style={{ width: '100%' }} />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Upload Dialog */}
            {showUploadDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-2xl">
                        <div className="flex items-center justify-between p-4 border-b border-border">
                            <h3 className="font-semibold flex items-center gap-2">
                                <Upload className="w-4 h-4" />
                                <span>Upload Knowledge Files</span>
                            </h3>
                            <button
                                onClick={() => setShowUploadDialog(false)}
                                className="p-1 rounded-md hover:bg-accent"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="p-6">
                            <div {...getRootProps()} className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? 'border-primary bg-primary/10' : 'border-border hover:border-primary'}`}>
                                <input {...getInputProps()} />
                                <div className="flex flex-col items-center gap-4">
                                    <Upload className="w-10 h-10 text-primary" />
                                    <h4 className="font-medium">Drag & Drop Files Here</h4>
                                    <p className="text-sm text-muted-foreground">
                                        or click to browse files
                                    </p>
                                    <p className="text-xs text-muted-foreground max-w-md">
                                        Supported formats: PDF, TXT, MD, JSON, CSV, JPG, PNG, MP4, JS, TS, PY, JAVA, C++
                                    </p>
                                    <button
                                        className="mt-4 flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            // This will trigger the file input
                                        }}
                                    >
                                        <Folder className="w-4 h-4" />
                                        <span>Browse Files</span>
                                    </button>
                                </div>
                            </div>

                            <div className="mt-6 p-4 bg-secondary rounded-md">
                                <h4 className="font-medium mb-2">File Processing Options:</h4>
                                <div className="space-y-3">
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Extract text content</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Create embeddings for semantic search</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" className="rounded" />
                                        <span className="text-sm">Chunk large documents (recommended)</span>
                                    </label>
                                    <label className="flex items-center gap-2">
                                        <input type="checkbox" defaultChecked className="rounded" />
                                        <span className="text-sm">Generate metadata automatically</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="border-t border-border p-4 flex justify-end gap-2">
                            <button
                                onClick={() => setShowUploadDialog(false)}
                                className="px-4 py-2 bg-secondary rounded-md hover:bg-secondary/80"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => {
                                    // This will be handled by the dropzone
                                    setShowUploadDialog(false)
                                }}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}