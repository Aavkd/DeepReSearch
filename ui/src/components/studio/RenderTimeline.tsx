import React from 'react';
import { TimelinePayload } from '@/types/structured';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RenderTimelineProps {
  data: TimelinePayload;
}

const RenderTimeline: React.FC<RenderTimelineProps> = ({ data }) => {
  // Group events by year for better organization
  const eventsByYear: Record<string, typeof data.events> = {};
  
  data.events.forEach(event => {
    const year = event.date.substring(0, 4);
    if (!eventsByYear[year]) {
      eventsByYear[year] = [];
    }
    eventsByYear[year].push(event);
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Timeline</h2>
      
      <div className="space-y-8">
        {Object.entries(eventsByYear).map(([year, events]) => (
          <div key={year}>
            <h3 className="text-xl font-bold text-yellow-300 mb-4">{year}</h3>
            <div className="space-y-4 pl-4 border-l-2 border-yellow-500/30">
              {events.map((event, index) => (
                <Card key={index} className="bg-white/5 border-white/10 ml-4">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold">
                      <span className="text-yellow-300">{event.date}</span> - {event.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div 
                      className="prose prose-invert max-w-none mb-3"
                      dangerouslySetInnerHTML={{ __html: event.summary_md }}
                    />
                    <div className="flex flex-wrap gap-2">
                      {event.source_urls.map((url, urlIndex) => (
                        <a
                          key={urlIndex}
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs bg-blue-900/50 hover:bg-blue-800/50 px-2 py-1 rounded"
                        >
                          Source {urlIndex + 1}
                        </a>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RenderTimeline;