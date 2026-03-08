import React, { useState, useEffect } from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import CodeBlock from '@tiptap/extension-code-block'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import { Bold, Italic, Code, Heading1, Heading2, Heading3, List, ListOrdered, Quote, Code as CodeIcon, Undo, Redo, Eye, EyeOff } from 'lucide-react'

interface MarkdownEditorProps {
    value: string
    onChange: (value: string) => void
    placeholder?: string
    className?: string
    showPreview?: boolean
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
    value,
    onChange,
    placeholder = 'Write your content here...',
    className = '',
    showPreview: initialShowPreview = false
}) => {
    const [showPreview, setShowPreview] = useState(initialShowPreview)
    const editor = useEditor({
        extensions: [
            StarterKit,
            CodeBlock,
            Placeholder.configure({
                placeholder: placeholder,
            }),
            CharacterCount,
        ],
        content: value,
        onUpdate: ({ editor }) => {
            const html = editor.getHTML()
            const markdown = convertHtmlToMarkdown(html)
            onChange(markdown)
        },
    })

    // Update editor content when value changes externally
    useEffect(() => {
        if (editor && editor.getHTML() !== value) {
            editor.commands.setContent(value)
        }
    }, [value, editor])

    // Simple HTML to Markdown converter
    const convertHtmlToMarkdown = (html: string): string => {
        // This is a simplified converter - in production you'd use a proper library
        let markdown = html

        // Convert headings
        markdown = markdown.replace(/<h1>(.*?)<\/h1>/g, '# $1\n\n')
        markdown = markdown.replace(/<h2>(.*?)<\/h2>/g, '## $1\n\n')
        markdown = markdown.replace(/<h3>(.*?)<\/h3>/g, '### $1\n\n')

        // Convert paragraphs
        markdown = markdown.replace(/<p>(.*?)<\/p>/g, '$1\n\n')

        // Convert bold
        markdown = markdown.replace(/<strong>(.*?)<\/strong>/g, '**$1**')

        // Convert italic
        markdown = markdown.replace(/<em>(.*?)<\/em>/g, '*$1*')

        // Convert code blocks
        markdown = markdown.replace(/<pre><code>(.*?)<\/code><\/pre>/gs, '```\n$1\n```\n\n')

        // Convert inline code
        markdown = markdown.replace(/<code>(.*?)<\/code>/g, '`$1`')

        // Convert lists
        markdown = markdown.replace(/<ul>(.*?)<\/ul>/gs, (_match: string, content: string) => {
            return content.replace(/<li>(.*?)<\/li>/g, '- $1\n').trim() + '\n\n'
        })

        markdown = markdown.replace(/<ol>(.*?)<\/ol>/gs, (_match: string, content: string) => {
            let index = 1
            return content.replace(/<li>(.*?)<\/li>/g, () => `${index++}. $1\n`).trim() + '\n\n'
        })

        // Convert blockquotes
        markdown = markdown.replace(/<blockquote>(.*?)<\/blockquote>/gs, (_match: string, content: string) => {
            return content.split('\n').map((line: string) => `> ${line}`).join('\n') + '\n\n'
        })

        // Remove remaining HTML angle brackets to avoid any leftover HTML tags
        // Escape HTML angle brackets to preserve them in markdown
        markdown = markdown.replace(/</g, '<').replace(/>/g, '>')

        // Clean up multiple newlines
        markdown = markdown.replace(/\n{3,}/g, '\n\n')

        return markdown.trim()
    }

    const togglePreview = () => {
        setShowPreview(!showPreview)
    }

    if (!editor) {
        return <div className={`border border-input rounded-md p-4 ${className}`}>Loading editor...</div>
    }

    return (
        <div className={`border border-input rounded-md overflow-hidden ${className}`}>
            <div className="flex items-center justify-between p-2 bg-secondary border-b border-border">
                <div className="flex items-center gap-1">
                    <button
                        onClick={() => editor.chain().focus().toggleBold().run()}
                        disabled={!editor.can().chain().focus().toggleBold().run()}
                        className={`p-1 rounded-md ${editor.isActive('bold') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Bold (Ctrl+B)"
                    >
                        <Bold className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleItalic().run()}
                        disabled={!editor.can().chain().focus().toggleItalic().run()}
                        className={`p-1 rounded-md ${editor.isActive('italic') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Italic (Ctrl+I)"
                    >
                        <Italic className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleCode().run()}
                        disabled={!editor.can().chain().focus().toggleCode().run()}
                        className={`p-1 rounded-md ${editor.isActive('code') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Inline Code (Ctrl+E)"
                    >
                        <Code className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                        className={`p-1 rounded-md ${editor.isActive('heading', { level: 1 }) ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Heading 1 (Ctrl+1)"
                    >
                        <Heading1 className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                        className={`p-1 rounded-md ${editor.isActive('heading', { level: 2 }) ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Heading 2 (Ctrl+2)"
                    >
                        <Heading2 className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
                        className={`p-1 rounded-md ${editor.isActive('heading', { level: 3 }) ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Heading 3 (Ctrl+3)"
                    >
                        <Heading3 className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleBulletList().run()}
                        className={`p-1 rounded-md ${editor.isActive('bulletList') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Bullet List (Ctrl+Shift+8)"
                    >
                        <List className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleOrderedList().run()}
                        className={`p-1 rounded-md ${editor.isActive('orderedList') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Numbered List (Ctrl+Shift+7)"
                    >
                        <ListOrdered className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleBlockquote().run()}
                        className={`p-1 rounded-md ${editor.isActive('blockquote') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Blockquote (Ctrl+Shift+B)"
                    >
                        <Quote className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().toggleCodeBlock().run()}
                        className={`p-1 rounded-md ${editor.isActive('codeBlock') ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                        title="Code Block (Ctrl+Alt+C)"
                    >
                        <CodeIcon className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().undo().run()}
                        disabled={!editor.can().chain().focus().undo().run()}
                        className="p-1 rounded-md hover:bg-accent"
                        title="Undo (Ctrl+Z)"
                    >
                        <Undo className="w-4 h-4" />
                    </button>

                    <button
                        onClick={() => editor.chain().focus().redo().run()}
                        disabled={!editor.can().chain().focus().redo().run()}
                        className="p-1 rounded-md hover:bg-accent"
                        title="Redo (Ctrl+Y)"
                    >
                        <Redo className="w-4 h-4" />
                    </button>
                </div>

                <button
                    onClick={togglePreview}
                    className={`p-1 rounded-md ${showPreview ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                    title="Toggle Preview (Ctrl+Shift+P)"
                >
                    {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
            </div>

            {showPreview ? (
                <div className="p-4 bg-background min-h-[200px] overflow-auto">
                    <MarkdownPreview content={value} />
                </div>
            ) : (
                <div className="p-4 min-h-[200px] overflow-auto prose dark:prose-invert max-w-none">
                    <EditorContent editor={editor} />
                </div>
            )}

            <div className="p-2 bg-secondary border-t border-border text-sm text-muted-foreground flex justify-between">
                <div>
                    Characters: {editor.storage.characterCount.characters()}
                </div>
                <div>
                    Words: {editor.storage.characterCount.words()}
                </div>
            </div>
        </div>
    )
}

interface MarkdownPreviewProps {
    content: string
}

const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({ content }) => {
    // Simple markdown to HTML converter for preview
    const renderMarkdown = (markdown: string): JSX.Element => {
        const lines = markdown.split('\n')
        const elements: JSX.Element[] = []

        let inCodeBlock = false
        let codeBlockContent = ''

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i]

            if (line.startsWith('```')) {
                if (inCodeBlock) {
                    // End code block
                    elements.push(
                        <pre key={`code-${i}`} className="bg-gray-100 dark:bg-gray-800 p-3 rounded-md overflow-x-auto">
                            <code>{codeBlockContent}</code>
                        </pre>
                    )
                    codeBlockContent = ''
                    inCodeBlock = false
                } else {
                    // Start code block
                    inCodeBlock = true
                }
                continue
            }

            if (inCodeBlock) {
                codeBlockContent += line + '\n'
                continue
            }

            if (line.startsWith('# ')) {
                elements.push(
                    <h1 key={`h1-${i}`} className="text-2xl font-bold mt-4 mb-2">{line.substring(2)}</h1>
                )
            } else if (line.startsWith('## ')) {
                elements.push(
                    <h2 key={`h2-${i}`} className="text-xl font-bold mt-3 mb-2">{line.substring(3)}</h2>
                )
            } else if (line.startsWith('### ')) {
                elements.push(
                    <h3 key={`h3-${i}`} className="text-lg font-bold mt-2 mb-1">{line.substring(4)}</h3>
                )
            } else if (line.startsWith('> ')) {
                elements.push(
                    <blockquote key={`quote-${i}`} className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-600 dark:text-gray-300 my-2">
                        {line.substring(2)}
                    </blockquote>
                )
            } else if (line.startsWith('- ') || line.startsWith('* ')) {
                elements.push(
                    <ul key={`ul-${i}`} className="list-disc list-inside my-1">
                        <li>{line.substring(2)}</li>
                    </ul>
                )
            } else if (line.match(/^\d+\. /)) {
                elements.push(
                    <ol key={`ol-${i}`} className="list-decimal list-inside my-1">
                        <li>{line.substring(line.indexOf('. ') + 2)}</li>
                    </ol>
                )
            } else if (line.startsWith('`') && line.endsWith('`')) {
                elements.push(
                    <code key={`code-inline-${i}`} className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                        {line.substring(1, line.length - 1)}
                    </code>
                )
            } else if (line.trim() === '') {
                elements.push(<br key={`br-${i}`} />)
            } else {
                elements.push(<p key={`p-${i}`} className="my-1">{line}</p>)
            }
        }

        return <>{elements}</>
    }

    return renderMarkdown(content)
}