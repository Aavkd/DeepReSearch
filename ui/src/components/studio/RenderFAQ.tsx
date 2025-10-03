import React from 'react';
import { FAQPayload } from '@/types/structured';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface RenderFAQProps {
  data: FAQPayload;
}

const RenderFAQ: React.FC<RenderFAQProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Frequently Asked Questions</h2>
      <div className="space-y-6">
        {data.items.map((item, index) => (
          <Card key={index} className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-blue-300">
                Q: {item.q}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div 
                className="prose prose-invert max-w-none"
                dangerouslySetInnerHTML={{ __html: item.a_md }}
              />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default RenderFAQ;