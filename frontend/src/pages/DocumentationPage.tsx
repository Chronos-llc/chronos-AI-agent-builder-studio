import React, { useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { 
  ChevronLeft, 
  Search, 
  Menu, 
  X, 
  BookOpen, 
  ArrowRight,
  Clock,
  FileText,
  Settings,
  Code,
  Mic2,
  Workflow
} from 'lucide-react'
import { MarkdownRenderer } from '../components/MarkdownRenderer'
import { 
  DOCUMENTATION_SECTIONS, 
  useDocumentationContent, 
  DocumentationSection,
} from '../services/documentationService'
import { ChronosLogo } from '../components/brand/ChronosLogo'

const DocumentationPage: React.FC = () => {
  const { sectionId, pageId } = useParams<{ sectionId: string; pageId: string }>()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // Find current section and page
  const currentSection = DOCUMENTATION_SECTIONS.find(section => section.id === sectionId)
  const currentPage = currentSection?.pages.find(page => page.id === pageId)

  const { content, loading, error } = useDocumentationContent(pageId || '')

  // Search functionality
  const filteredSections = DOCUMENTATION_SECTIONS.map(section => ({
    ...section,
    pages: section.pages.filter(page => 
      page.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      page.description.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(section => section.pages.length > 0)

  // Get section icon
  const getSectionIcon = (sectionId: string) => {
    switch (sectionId) {
      case 'overview':
        return <BookOpen className="h-4 w-4" />
      case 'agent-builder':
        return <Settings className="h-4 w-4" />
      case 'agent-suite':
        return <FileText className="h-4 w-4" />
      case 'integrations':
        return <Code className="h-4 w-4" />
      case 'workflow':
        return <Workflow className="h-4 w-4" />
      case 'voice':
        return <Mic2 className="h-4 w-4" />
      case 'api':
        return <Code className="h-4 w-4" />
      case 'advanced':
        return <Clock className="h-4 w-4" />
      default:
        return <BookOpen className="h-4 w-4" />
    }
  }

  if (!currentSection || !currentPage) {
    return (
      <div className="min-h-screen bg-[#06080D] text-white">
        <div className="mx-auto w-full max-w-7xl px-6 py-8">
          <header className="mb-8 flex items-center justify-between">
            <ChronosLogo textClassName="text-white" markClassName="text-white" />
            <Link 
              to="/docs" 
              className="inline-flex items-center gap-2 rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 hover:border-white/40 hover:text-white"
            >
              <ChevronLeft className="h-4 w-4" />
              Back to Docs Hub
            </Link>
          </header>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 text-center">
            <h1 className="text-2xl font-semibold mb-2">Page Not Found</h1>
            <p className="text-white/75 mb-6">The documentation page you're looking for doesn't exist or has been moved.</p>
            <Link 
              to="/docs" 
              className="inline-flex items-center gap-2 rounded-full bg-white px-6 py-2 text-sm font-semibold text-[#070A10] hover:bg-white/90"
            >
              <ChevronLeft className="h-4 w-4" />
              Back to Docs Hub
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#06080D] text-white">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="mx-auto w-full max-w-7xl px-6 py-8">
        <header className="mb-6 flex items-center justify-between">
          <ChronosLogo textClassName="text-white" markClassName="text-white" />
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden p-2 rounded-full border border-white/20 text-white/80 hover:border-white/40 hover:text-white"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </button>
            <Link 
              to="/docs" 
              className="hidden lg:inline-flex items-center gap-2 rounded-full border border-white/20 px-4 py-2 text-sm text-white/80 hover:border-white/40 hover:text-white"
            >
              <ChevronLeft className="h-4 w-4" />
              Back to Docs Hub
            </Link>
          </div>
        </header>

        <div className="flex gap-6">
          {/* Sidebar navigation */}
          <aside className={`
            fixed inset-y-0 left-0 z-50 w-80 bg-[#06080D] border-r border-white/10 transform transition-transform duration-300 lg:static lg:transform-none
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          `}>
            <div className="p-6">
              <button
                className="lg:hidden absolute top-6 right-6 p-2 rounded-full border border-white/20 text-white/80 hover:border-white/40 hover:text-white"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-5 w-5" />
              </button>

              {/* Search */}
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-white/50" />
                <input
                  type="text"
                  placeholder="Search documentation..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-white/50 focus:outline-none focus:border-cyan-500 focus:bg-white/10"
                />
              </div>

              {/* Navigation */}
              <nav className="space-y-6">
                {filteredSections.map((section) => (
                  <div key={section.id} className="space-y-2">
                    <h3 className="text-xs font-semibold text-white/60 uppercase tracking-wide">
                      {section.title}
                    </h3>
                    <ul className="space-y-1">
                      {section.pages.map((page) => (
                        <li key={page.id}>
                          <Link
                            to={`/docs/${section.id}/${page.id}`}
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                              section.id === sectionId && page.id === pageId
                                ? 'bg-white/10 text-white border border-white/10'
                                : 'text-white/75 hover:bg-white/5 hover:text-white'
                            }`}
                            onClick={() => setSidebarOpen(false)}
                          >
                            {page.title}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </nav>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 min-w-0">
            {/* Breadcrumb */}
            <nav className="mb-6 flex items-center gap-2 text-sm text-white/60">
              <Link 
                to="/docs" 
                className="hover:text-white transition-colors"
              >
                Docs Hub
              </Link>
              <span className="text-white/30">/</span>
              <Link 
                to={`/docs/${currentSection.id}`} 
                className="hover:text-white transition-colors"
              >
                {currentSection.title}
              </Link>
              <span className="text-white/30">/</span>
              <span className="text-white">{currentPage.title}</span>
            </nav>

            {/* Page header */}
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                {getSectionIcon(currentSection.id)}
                <h1 className="text-2xl font-semibold">{currentPage.title}</h1>
              </div>
              <p className="text-white/75">{currentPage.description}</p>
            </div>

            {/* Loading state */}
            {loading && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-white/20 border-t-white mb-4"></div>
                <p className="text-white/75">Loading documentation...</p>
              </div>
            )}

            {/* Error state */}
            {error && (
              <div className="rounded-2xl border border-red-500/30 bg-red-500/5 p-6">
                <h3 className="text-red-200 font-medium mb-2">Error Loading Documentation</h3>
                <p className="text-red-100/75">{error}</p>
              </div>
            )}

            {/* Documentation content */}
            {!loading && !error && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 md:p-8">
                <MarkdownRenderer content={content} />
              </div>
            )}

            {/* Next/Previous navigation */}
            {!loading && !error && (
              <div className="mt-8 flex justify-between items-center">
                <div>
                  {currentSection.pages.findIndex(page => page.id === pageId) > 0 && (
                    <Link
                      to={`/docs/${currentSection.id}/${currentSection.pages[currentSection.pages.findIndex(page => page.id === pageId) - 1].id}`}
                      className="inline-flex items-center gap-2 text-sm text-white/75 hover:text-white transition-colors"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous: {currentSection.pages[currentSection.pages.findIndex(page => page.id === pageId) - 1].title}
                    </Link>
                  )}
                </div>
                <div className="text-right">
                  {currentSection.pages.findIndex(page => page.id === pageId) < currentSection.pages.length - 1 && (
                    <Link
                      to={`/docs/${currentSection.id}/${currentSection.pages[currentSection.pages.findIndex(page => page.id === pageId) + 1].id}`}
                      className="inline-flex items-center gap-2 text-sm text-white/75 hover:text-white transition-colors"
                    >
                      Next: {currentSection.pages[currentSection.pages.findIndex(page => page.id === pageId) + 1].title}
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  )}
                </div>
              </div>
            )}

            {/* Footer */}
            <footer className="mt-12 border-t border-white/10 pt-6 text-center text-sm text-white/50">
              <p>Chronos Studio Documentation • Last updated: {new Date().toLocaleDateString()}</p>
              <p className="mt-1">Need help? <Link to="/app/support" className="text-cyan-300 hover:text-cyan-200">Contact Support</Link></p>
            </footer>
          </main>
        </div>
      </div>
    </div>
  )
}

export default DocumentationPage