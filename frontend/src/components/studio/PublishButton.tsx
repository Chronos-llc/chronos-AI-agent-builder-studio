import { useState } from 'react';
import { Button } from '../ui/button';
import { Upload, Check } from 'lucide-react';
import { PublishModal } from './PublishModal';

interface PublishButtonProps {
    agentId: number;
    agentName: string;
    className?: string;
}

export const PublishButton = ({
    agentId,
    agentName,
    className = ''
}: PublishButtonProps) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isPublished, setIsPublished] = useState(false);

    const handlePublishSuccess = () => {
        setIsPublished(true);
        // Reset published state after 3 seconds
        setTimeout(() => setIsPublished(false), 3000);
    };

    return (
        <>
            <Button
                onClick={() => setIsModalOpen(true)}
                className={className}
                disabled={isPublished}
            >
                {isPublished ? (
                    <>
                        <Check className="w-4 h-4 mr-2" />
                        Published
                    </>
                ) : (
                    <>
                        <Upload className="w-4 h-4 mr-2" />
                        Publish
                    </>
                )}
            </Button>

            <PublishModal
                agentId={agentId}
                agentName={agentName}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onPublishSuccess={handlePublishSuccess}
            />
        </>
    );
};