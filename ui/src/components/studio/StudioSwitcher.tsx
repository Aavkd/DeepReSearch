import React, { useState } from 'react';
import { Button } from "@/components/ui/button";

interface StudioSwitcherProps {
  value: string;
  onValueChange: (value: string) => void;
}

const StudioSwitcher: React.FC<StudioSwitcherProps> = ({ value, onValueChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const outputTypes = [
    { value: 'answer', label: 'Default Answer' },
    { value: 'faq', label: 'FAQ' },
    { value: 'study_guide', label: 'Study Guide' },
    { value: 'briefing_doc', label: 'Briefing Document' },
    { value: 'timeline', label: 'Timeline' },
    { value: 'mind_map', label: 'Mind Map' },
  ];

  const currentLabel = outputTypes.find(type => type.value === value)?.label || 'Select output type';

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm font-medium">Output Type:</span>
      <div className="relative">
        <Button 
          variant="outline" 
          className="w-[180px] justify-between"
          onClick={() => setIsOpen(!isOpen)}
        >
          {currentLabel}
          <span className="ml-2">▼</span>
        </Button>
        
        {isOpen && (
          <div className="absolute top-full left-0 mt-1 w-full bg-black border border-white/10 rounded-md shadow-lg z-10">
            {outputTypes.map((type) => (
              <button
                key={type.value}
                className="block w-full text-left px-4 py-2 text-sm hover:bg-white/10"
                onClick={() => {
                  onValueChange(type.value);
                  setIsOpen(false);
                }}
              >
                {type.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudioSwitcher;