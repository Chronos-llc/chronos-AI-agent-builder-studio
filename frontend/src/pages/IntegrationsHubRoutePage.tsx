import { useNavigate } from 'react-router-dom'
import ChronosHubModal from '../components/integrations/ChronosHubModal'

const IntegrationsHubRoutePage = () => {
  const navigate = useNavigate()

  const handleClose = () => {
    if (window.history.length > 1) {
      navigate(-1)
      return
    }
    navigate('/app/integrations', { replace: true })
  }

  return (
    <div className="relative -mx-6 -my-8 min-h-[calc(100vh-6rem)] bg-background/90 p-4 md:p-6">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent" />
      <div className="relative">
        <ChronosHubModal onClose={handleClose} />
      </div>
    </div>
  )
}

export default IntegrationsHubRoutePage
