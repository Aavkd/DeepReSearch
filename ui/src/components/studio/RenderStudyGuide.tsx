import React from 'react';
import { StudyGuidePayload } from '@/types/structured';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface RenderStudyGuideProps {
  data: StudyGuidePayload;
}

const RenderStudyGuide: React.FC<RenderStudyGuideProps> = ({ data }) => {
  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">Study Guide</h2>
      
      {data.modules.map((module, moduleIndex) => (
        <Card key={moduleIndex} className="bg-white/5 border-white/10">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-green-300">
              Module {moduleIndex + 1}: {module.title}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Notes */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Notes</h3>
              <div 
                className="prose prose-invert max-w-none bg-black/20 p-4 rounded-lg"
                dangerouslySetInnerHTML={{ __html: module.notes_md }}
              />
            </div>
            
            {/* Quiz */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Quiz</h3>
              <div className="space-y-4">
                {module.quiz.map((quizItem, quizIndex) => (
                  <div key={quizIndex} className="border-b border-white/10 pb-3">
                    <p className="font-medium">Q{quizIndex + 1}: {quizItem.question}</p>
                    <div 
                      className="mt-1 text-white/80"
                      dangerouslySetInnerHTML={{ __html: quizItem.answer_md }}
                    />
                  </div>
                ))}
              </div>
            </div>
            
            {/* Glossary */}
            <div>
              <h3 className="text-lg font-semibold mb-2">Glossary</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {module.glossary.map((glossaryItem, glossaryIndex) => (
                  <Card key={glossaryIndex} className="bg-black/20 border-white/10">
                    <CardContent className="p-4">
                      <Badge variant="secondary" className="mb-2 bg-blue-900/50">
                        Term
                      </Badge>
                      <h4 className="font-bold text-blue-300">{glossaryItem.term}</h4>
                      <div 
                        className="mt-2 text-sm"
                        dangerouslySetInnerHTML={{ __html: glossaryItem.def_md }}
                      />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default RenderStudyGuide;