import React, { useState } from 'react';
import { Copy, Check, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { toast } from 'react-hot-toast';

interface MessagingAPIIntegrationDetailsProps {
  integration: any;
  onInstall: () => void;
}

export const MessagingAPIIntegrationDetails: React.FC<MessagingAPIIntegrationDetailsProps> = ({
  integration,
  onInstall
}) => {
  const [activeTab, setActiveTab] = useState<'info' | 'configuration'>('info');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [copiedItem, setCopiedItem] = useState<string | null>(null);

  const copyToClipboard = async (text: string, item: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItem(item);
      toast.success('Copied to clipboard');
      setTimeout(() => setCopiedItem(null), 2000);
    } catch (error) {
      toast.error('Failed to copy');
    }
  };

  const handleSaveConfiguration = () => {
    if (!webhookUrl.trim()) {
      toast.error('Please enter a webhook URL');
      return;
    }
    toast.success('Configuration saved successfully');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center">
            <span className="text-3xl">{integration.icon || '💬'}</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold">{integration.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-sm text-muted-foreground">by {integration.author || 'plus'}</span>
              <Badge variant="secondary">v{integration.version}</Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Copy className="w-4 h-4 mr-2" />
            Copy Share Link
          </Button>
        </div>
      </div>

      {/* Install Button */}
      <Button onClick={onInstall} className="w-full" size="lg">
        Install Integration
      </Button>

      {/* Status Alert */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-blue-900 font-medium">
                Something is missing or not working as expected with Messaging API?
              </p>
              <button className="text-sm text-blue-600 hover:underline mt-1">
                Request changes
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="border-b border-border">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('info')}
            className={`pb-2 px-1 border-b-2 transition-colors ${
              activeTab === 'info'
                ? 'border-primary text-primary font-medium'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Info
          </button>
          <button
            onClick={() => setActiveTab('configuration')}
            className={`pb-2 px-1 border-b-2 transition-colors ${
              activeTab === 'configuration'
                ? 'border-primary text-primary font-medium'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Configuration
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'info' && (
        <div className="space-y-6">
          {/* How it works */}
          <Card>
            <CardHeader>
              <CardTitle>How it works</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                To send messages to your bot, use the API endpoint. When sending messages to your bot, you provide a
                conversationId parameter that will be sent back to your webhook url, so that you may identify where to send your
                bot's responses.
              </p>
              <p className="text-sm text-muted-foreground">
                To handle responses from your bot, you provide an endpoint url. Each request sent to this endpoint carries a single
                bot message, and includes the conversationId that was previously provided. Depending on your bot, you could
                receive multiple responses, or no responses at all.
              </p>
            </CardContent>
          </Card>

          {/* Getting started */}
          <Card>
            <CardHeader>
              <CardTitle>Getting started</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-muted/50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Pre-requisites</h4>
                <p className="text-sm text-muted-foreground">
                  All you need is an endpoint to catch your bot's responses that returns http status 200. For trying this out, we
                  recommend a free endpoint on Request Bin.
                </p>
              </div>

              <div>
                <h4 className="font-medium mb-3">Steps</h4>
                <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
                  <li>Click <strong>Install</strong> on the top right and select your bot.</li>
                  <li>Click the popup that appears to configure your integration.</li>
                  <li>Add the url that points to your server's endpoint in the <strong>Response Endpoint URL</strong> field.</li>
                  <li>Copy the Webhook URL at the top of the page, this will be the endpoint for creating messages. Save this for later.</li>
                  <li>In Chronos, click your avatar on the top right, then <strong>Personal Access Tokens</strong>. Create a new token and save it for later.</li>
                  <li>Send an http request with the following content:</li>
                </ol>
              </div>

              <div className="space-y-3 mt-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">Endpoint:</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard('(INTEGRATION_WEBHOOK_URL)', 'endpoint')}
                    >
                      {copiedItem === 'endpoint' ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  <code className="block bg-muted p-2 rounded text-xs">(INTEGRATION_WEBHOOK_URL)</code>
                </div>

                <div>
                  <span className="text-sm font-medium">Method:</span>
                  <code className="block bg-muted p-2 rounded text-xs mt-1">POST</code>
                </div>

                <div>
                  <span className="text-sm font-medium">Headers:</span>
                  <div className="bg-muted p-2 rounded text-xs mt-1 space-y-1">
                    <div>• Authorization: bearer <strong>(PERSONAL_ACCESS_TOKEN)</strong></div>
                  </div>
                </div>

                <div>
                  <span className="text-sm font-medium">Body:</span>
                  <div className="bg-muted p-3 rounded text-xs mt-1 space-y-1">
                    <div>• <strong>userId:</strong> (string, required) ensures that the message is added for the correct user, in case of multiple users</div>
                    <div>• <strong>messageId:</strong> (string, required) helps prevent duplicates</div>
                    <div>• <strong>conversationId:</strong> (string, required) identifies the conversation uniquely and is used for sending back responses</div>
                    <div>• <strong>type:</strong> (string, required) should be 'text' if the message type is text, otherwise a different string for other types</div>
                    <div>• <strong>text:</strong> (string, required) the text of the user's message if the type is text, or a summary of the payload for other types</div>
                    <div>• <strong>payload:</strong> (any, required) an object containing any data you want to send, specific to the message type</div>
                  </div>
                </div>
              </div>

              <div className="mt-4">
                <p className="text-sm text-muted-foreground mb-2">
                  7. On your server, handle the response (make sure your bot is published and responds to messages). The request body should look like this:
                </p>
                <div className="bg-muted p-3 rounded text-xs space-y-1">
                  <div>• <strong>type:</strong> (string, required) specifies the type of the message</div>
                  <div>• <strong>payload:</strong> (any, required) contains the response text or metadata otherwise</div>
                  <div>• <strong>conversationId:</strong> (string, required) use this to send the response to the correct location</div>
                  <div>• <strong>chronosUserId:</strong> (string, required) Chronos user ID for debugging purposes</div>
                  <div>• <strong>chronosMessageId:</strong> (string, required) Chronos message ID for debugging purposes</div>
                  <div>• <strong>chronosConversationId:</strong> (string, required) Chronos conversation ID for debugging purposes</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Cards */}
          <Card>
            <CardHeader>
              <CardTitle>Action Cards</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Additional action cards and features will be available after installation.
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'configuration' && (
        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Response Endpoint URL <span className="text-destructive">*</span>
              </label>
              <Input
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://your-server.com/webhook"
                className="w-full"
              />
              <p className="text-xs text-muted-foreground mt-1">
                The bot will send its messages to this URL
              </p>
            </div>

            <Button onClick={handleSaveConfiguration} className="w-full">
              Save Configuration
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MessagingAPIIntegrationDetails;
