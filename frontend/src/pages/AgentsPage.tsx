import React from 'react'
import { Link } from 'react-router-dom'

const AgentsPage: React.FC = () => {
    return (
        <div className="page-container">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">My Agents</h1>
                <Link to="/agents/new" className="btn btn-primary">
                    Create New Agent
                </Link>
            </div>

            <div className="card p-8 text-center">
                <h2 className="text-xl font-semibold mb-2">No agents yet</h2>
                <p className="text-gray-600 mb-4">
                    Get started by creating your first AI agent
                </p>
                <Link to="/agents/new" className="btn btn-primary">
                    Create Agent
                </Link>
            </div>
        </div>
    )
}

export default AgentsPage