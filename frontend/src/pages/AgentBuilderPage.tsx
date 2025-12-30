import React from 'react'
import { useParams } from 'react-router-dom'
import { StudioLayout } from '../components/studio/StudioLayout'

const AgentBuilderPage: React.FC = () => {
    const { id } = useParams()

    return (
        <div className="h-screen w-full">
            <StudioLayout />
        </div>
    )
}

export default AgentBuilderPage