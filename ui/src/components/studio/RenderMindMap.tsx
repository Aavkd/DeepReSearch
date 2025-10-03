import React, { useState } from 'react';
import { MindMapPayload, MindMapNode } from '@/types/structured';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronRight } from "lucide-react";

interface MindMapNodeProps {
  node: MindMapNode;
  level: number;
}

const MindMapNodeComponent: React.FC<MindMapNodeProps> = ({ node, level }) => {
  const [isExpanded, setIsExpanded] = useState(level < 2); // Expand first two levels by default
  
  if (!node.children || node.children.length === 0) {
    return (
      <div className="ml-4 py-1">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
          <span className="text-sm">{node.label}</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="ml-4">
      <div 
        className="flex items-center py-1 cursor-pointer hover:bg-white/5 rounded"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 mr-2">
          {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </Button>
        <div className="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
        <span className="font-medium">{node.label}</span>
        <span className="text-xs text-white/50 ml-2">({node.children.length})</span>
      </div>
      
      {isExpanded && (
        <div className="border-l border-white/20 ml-2 pl-3 mt-1">
          {node.children.map((child, index) => (
            <MindMapNodeComponent key={index} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

interface RenderMindMapProps {
  data: MindMapPayload;
}

const RenderMindMap: React.FC<RenderMindMapProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Mind Map</h2>
      
      <Card className="bg-white/5 border-white/10">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-cyan-300">
            {data.nodes[0]?.label || "Mind Map"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="p-4">
            {data.nodes.map((node, index) => (
              <MindMapNodeComponent key={index} node={node} level={0} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RenderMindMap;