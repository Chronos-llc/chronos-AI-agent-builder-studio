import React, { useState, useEffect } from 'react';
import { Plus, Copy, Trash2, Key, AlertCircle, Check } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import axios from 'axios';
import { toast } from 'react-hot-toast';

interface PersonalAccessToken {
  id: number;
  name: string;
  token_prefix: string;
  scopes: string | null;
  last_used_at: string | null;
  expires_at: string | null;
  is_active: boolean;
  is_revoked: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

interface NewToken extends PersonalAccessToken {
  token: string;
}

export const PersonalAccessTokens: React.FC = () => {
  const [tokens, setTokens] = useState<PersonalAccessToken[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTokenName, setNewTokenName] = useState('');
  const [newlyCreatedToken, setNewlyCreatedToken] = useState<string | null>(null);
  const [copiedToken, setCopiedToken] = useState(false);

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/v1/personal-access-tokens/tokens/');
      setTokens(response.data.tokens);
    } catch (error) {
      console.error('Error fetching tokens:', error);
      toast.error('Failed to load tokens');
    } finally {
      setIsLoading(false);
    }
  };

  const createToken = async () => {
    if (!newTokenName.trim()) {
      toast.error('Please enter a token name');
      return;
    }

    try {
      const response = await axios.post<NewToken>('/api/v1/personal-access-tokens/tokens/', {
        name: newTokenName,
        scopes: null,
        expires_at: null
      });
      
      setNewlyCreatedToken(response.data.token);
      setNewTokenName('');
      await fetchTokens();
      toast.success('Token created successfully');
    } catch (error) {
      console.error('Error creating token:', error);
      toast.error('Failed to create token');
    }
  };

  const revokeToken = async (tokenId: number) => {
    if (!confirm('Are you sure you want to revoke this token? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.post(`/api/v1/personal-access-tokens/tokens/${tokenId}/revoke`);
      await fetchTokens();
      toast.success('Token revoked successfully');
    } catch (error) {
      console.error('Error revoking token:', error);
      toast.error('Failed to revoke token');
    }
  };

  const deleteToken = async (tokenId: number) => {
    if (!confirm('Are you sure you want to delete this token? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`/api/v1/personal-access-tokens/tokens/${tokenId}`);
      await fetchTokens();
      toast.success('Token deleted successfully');
    } catch (error) {
      console.error('Error deleting token:', error);
      toast.error('Failed to delete token');
    }
  };

  const copyToken = async (token: string) => {
    try {
      await navigator.clipboard.writeText(token);
      setCopiedToken(true);
      toast.success('Token copied to clipboard');
      setTimeout(() => setCopiedToken(false), 2000);
    } catch (error) {
      toast.error('Failed to copy token');
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Personal Access Tokens</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your personal access tokens for API authentication
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create New Token
        </Button>
      </div>

      {/* Create Token Modal */}
      {showCreateModal && (
        <Card className="border-primary">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="w-5 h-5" />
              Create New Personal Access Token
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!newlyCreatedToken ? (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">Token Name</label>
                  <Input
                    value={newTokenName}
                    onChange={(e) => setNewTokenName(e.target.value)}
                    placeholder="e.g., Production Bot Integration"
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Choose a descriptive name to help you identify this token later
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button onClick={createToken} className="flex-1">
                    Create Token
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setShowCreateModal(false);
                      setNewTokenName('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-medium text-yellow-900">Important: Save your token now</p>
                      <p className="text-sm text-yellow-700 mt-1">
                        You won't be able to see this token again. Make sure to copy it and store it securely.
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Your New Token</label>
                  <div className="flex gap-2">
                    <Input
                      value={newlyCreatedToken}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      onClick={() => copyToken(newlyCreatedToken)}
                    >
                      {copiedToken ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
                <Button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewlyCreatedToken(null);
                  }}
                  className="w-full"
                >
                  Done
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tokens List */}
      {isLoading ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">Loading tokens...</p>
        </div>
      ) : tokens.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <Key className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">No tokens yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Create your first personal access token to start using the Chronos API
            </p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Token
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {tokens.map((token) => (
            <Card key={token.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-medium">{token.name}</h3>
                      {token.is_revoked ? (
                        <Badge variant="destructive">Revoked</Badge>
                      ) : token.is_active ? (
                        <Badge variant="default">Active</Badge>
                      ) : (
                        <Badge variant="secondary">Inactive</Badge>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                      <div>
                        <span className="font-medium">Token:</span>{' '}
                        <code className="bg-muted px-1 py-0.5 rounded">{token.token_prefix}...</code>
                      </div>
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(token.created_at)}
                      </div>
                      <div>
                        <span className="font-medium">Last used:</span> {formatDate(token.last_used_at)}
                      </div>
                      <div>
                        <span className="font-medium">Usage count:</span> {token.usage_count}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    {!token.is_revoked && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => revokeToken(token.id)}
                      >
                        Revoke
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteToken(token.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default PersonalAccessTokens;
