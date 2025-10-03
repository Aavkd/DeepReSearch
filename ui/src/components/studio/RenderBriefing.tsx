import React from 'react';
import { BriefingPayload } from '@/types/structured';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RenderBriefingProps {
  data: BriefingPayload;
}

const RenderBriefing: React.FC<RenderBriefingProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Briefing Document</h2>
      
      {data.sections.map((section, index) => (
        <Card key={index} className="bg-white/5 border-white/10">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-purple-300">
              {section.heading}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {section.content_md && (
              <div 
                className="prose prose-invert max-w-none mb-4"
                dangerouslySetInnerHTML={{ __html: section.content_md }}
              />
            )}
            
            {section.items && section.items.length > 0 && (
              <ul className="list-disc pl-6 space-y-2">
                {section.items.map((item, itemIndex) => (
                  <li key={itemIndex} className="text-white/90">
                    {item}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default RenderBriefing;