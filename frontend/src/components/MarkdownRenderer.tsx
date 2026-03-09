import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeRaw from 'rehype-raw'

interface MarkdownRendererProps {
  content: string
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="markdown-content prose prose-invert prose-sm md:prose-base lg:prose-lg max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeRaw]}
        components={{
          h1: ({ ...props }) => (
            <h1 
              className="mt-8 mb-4 text-3xl font-bold text-white border-b border-white/10 pb-2"
              {...props}
            />
          ),
          h2: ({ ...props }) => (
            <h2 
              className="mt-6 mb-3 text-2xl font-semibold text-white border-b border-white/5 pb-1"
              {...props}
            />
          ),
          h3: ({ ...props }) => (
            <h3 
              className="mt-5 mb-2 text-xl font-medium text-white"
              {...props}
            />
          ),
          h4: ({ ...props }) => (
            <h4 
              className="mt-4 mb-2 text-lg font-medium text-white"
              {...props}
            />
          ),
          p: ({ ...props }) => (
            <p 
              className="mt-2 mb-2 text-white/85 leading-relaxed"
              {...props}
            />
          ),
          ul: ({ ...props }) => (
            <ul 
              className="mt-2 mb-2 ml-5 list-disc text-white/85"
              {...props}
            />
          ),
          ol: ({ ...props }) => (
            <ol 
              className="mt-2 mb-2 ml-5 list-decimal text-white/85"
              {...props}
            />
          ),
          li: ({ ...props }) => (
            <li 
              className="mt-1 mb-1 text-white/85"
              {...props}
            />
          ),
          blockquote: ({ ...props }) => (
            <blockquote 
              className="mt-4 mb-4 border-l-4 border-cyan-500 pl-4 italic text-white/75 bg-white/5 py-2 px-3 rounded-r"
              {...props}
            />
          ),
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '')
            return match ? (
              <div className="mt-4 mb-4 rounded-lg overflow-hidden">
                <div className="bg-white/10 px-4 py-2 border-b border-white/10 text-xs text-white/60">
                  {match[1]}
                </div>
                <pre className="bg-black/50 p-4 overflow-x-auto">
                  <code className={className} {...props}>
                    {children}
                  </code>
                </pre>
              </div>
            ) : (
              <code 
                className="bg-white/10 px-1.5 py-0.5 rounded text-cyan-200 text-sm"
                {...props}
              >
                {children}
              </code>
            )
          },
          a: ({ ...props }) => (
            <a 
              className="text-cyan-300 hover:text-cyan-200 underline underline-offset-2"
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            />
          ),
          table: ({ ...props }) => (
            <div className="mt-4 mb-4 overflow-x-auto">
              <table 
                className="min-w-full border-collapse border border-white/10"
                {...props}
              />
            </div>
          ),
          thead: ({ ...props }) => (
            <thead 
              className="bg-white/5"
              {...props}
            />
          ),
          tbody: ({ ...props }) => (
            <tbody 
              className="text-white/85"
              {...props}
            />
          ),
          tr: ({ ...props }) => (
            <tr 
              className="border-b border-white/5"
              {...props}
            />
          ),
          th: ({ ...props }) => (
            <th 
              className="px-4 py-2 text-left font-semibold text-white border-r border-white/10 last:border-r-0"
              {...props}
            />
          ),
          td: ({ ...props }) => (
            <td 
              className="px-4 py-2 text-left text-white/85 border-r border-white/10 last:border-r-0"
              {...props}
            />
          ),
          img: ({ ...props }) => (
            <img 
              className="mt-4 mb-4 rounded-lg shadow-lg max-w-full h-auto"
              {...props}
            />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}