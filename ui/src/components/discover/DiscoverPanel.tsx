import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import { DiscoverResponse } from '@/types/structured';

interface DiscoverPanelProps {
  onAddToSession: (url: string) => void;
}

const DiscoverPanel: React.FC<DiscoverPanelProps> = ({ onAddToSession }) => {
  const [topic, setTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<DiscoverResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDiscover = async () => {
    if (!topic.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await fetch('/api/discover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          maxSources: 10,
          timeRange: '365d',
          locale: 'en'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }
      
      const data: DiscoverResponse = await response.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Failed to discover sources');
      console.error('Discover error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const domainOf = (url: string) => {
    try {
      const u = new URL(url);
      return u.hostname.replace(/^www\./, "");
    } catch {
      return url;
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Discover Sources</h2>
        <p className="text-white/70 mb-6">
          Find authoritative sources and research materials for your topic
        </p>
        
        <div className="max-w-2xl mx-auto flex gap-2">
          <Input
            placeholder="Describe your topic..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleDiscover()}
            className="flex-1"
          />
          <Button 
            onClick={handleDiscover} 
            disabled={isLoading || !topic.trim()}
            className="whitespace-nowrap"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Discovering...
              </>
            ) : (
              'Discover'
            )}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="bg-red-500/10 border-red-500/30">
          <CardContent className="p-4">
            <div className="font-semibold mb-1">Error</div>
            <div className="opacity-90">{error}</div>
          </CardContent>
        </Card>
      )}

      {results && (
        <div className="space-y-4">
          <div className="text-sm text-white/60">
            Planned search queries: {results.queries_planned.join(', ')}
          </div>
          
          <div className="space-y-4">
            {results.recommendations.map((rec, index) => (
              <Card key={index} className="bg-white/5 border-white/10">
                <CardHeader>
                  <CardTitle className="text-lg">
                    <a 
                      href={rec.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-300 hover:underline"
                    >
                      {rec.title}
                    </a>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm text-white/60">
                    {domainOf(rec.url)}
                    {rec.published && ` • ${new Date(rec.published).toLocaleDateString()}`}
                  </div>
                  
                  <div 
                    className="prose prose-invert max-w-none text-sm"
                    dangerouslySetInnerHTML={{ __html: rec.why_md }}
                  />
                  
                  <div 
                    className="prose prose-invert max-w-none text-sm bg-black/20 p-3 rounded"
                    dangerouslySetInnerHTML={{ __html: rec.summary_md }}
                  />
                  
                  <div className="flex flex-wrap gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => onAddToSession(rec.url)}
                    >
                      Add to Session
                    </Button>
                    <a 
                      href={rec.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      <Button variant="outline" size="sm">
                        Open Link
                      </Button>
                    </a>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DiscoverPanel;