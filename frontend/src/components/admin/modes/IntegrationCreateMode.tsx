import React, { useState } from 'react';
import { adminIntegrationService, CreateIntegrationPayload } from '../../../services/adminIntegrationService';

interface IntegrationCreateModeProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

const IntegrationCreateMode: React.FC<IntegrationCreateModeProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<CreateIntegrationPayload>({
    name: '',
    description: '',
    category: '',
    publisher: '',
    version: '1.0.0',
    icon_url: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      await adminIntegrationService.createIntegration(formData);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create integration');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Create New Integration</h2>
      
      {error && (
        <div className="bg-destructive/10 text-destructive border border-destructive/20 rounded-md p-3 mb-4" role="alert">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">
            Name <span className="text-destructive">*</span>
          </label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Integration name"
          />
        </div>
        
        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-1">
            Description <span className="text-destructive">*</span>
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={3}
            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Describe the integration"
          />
        </div>
        
        <div>
          <label htmlFor="category" className="block text-sm font-medium mb-1">
            Category <span className="text-destructive">*</span>
          </label>
          <select
            id="category"
            name="category"
            value={formData.category}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Select a category</option>
            <option value="communication">Communication</option>
            <option value="productivity">Productivity</option>
            <option value="analytics">Analytics</option>
            <option value="storage">Storage</option>
            <option value="security">Security</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div>
          <label htmlFor="publisher" className="block text-sm font-medium mb-1">
            Publisher
          </label>
          <input
            id="publisher"
            name="publisher"
            type="text"
            value={formData.publisher}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Publisher name"
          />
        </div>
        
        <div>
          <label htmlFor="version" className="block text-sm font-medium mb-1">
            Version
          </label>
          <input
            id="version"
            name="version"
            type="text"
            value={formData.version}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="1.0.0"
          />
        </div>
        
        <div>
          <label htmlFor="icon_url" className="block text-sm font-medium mb-1">
            Icon URL
          </label>
          <input
            id="icon_url"
            name="icon_url"
            type="url"
            value={formData.icon_url}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="https://example.com/icon.png"
          />
        </div>
        
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Creating...' : 'Create Integration'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-input rounded-md hover:bg-accent transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default IntegrationCreateMode;
