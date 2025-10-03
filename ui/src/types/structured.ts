// Structured content types matching the backend schemas

export interface FAQItem {
  q: string;
  a_md: string;
}

export interface FAQPayload {
  type: "faq";
  version: string;
  items: FAQItem[];
}

export interface StudyGuideQuizItem {
  question: string;
  answer_md: string;
}

export interface StudyGuideGlossaryItem {
  term: string;
  def_md: string;
}

export interface StudyGuideModule {
  title: string;
  notes_md: string;
  quiz: StudyGuideQuizItem[];
  glossary: StudyGuideGlossaryItem[];
}

export interface StudyGuidePayload {
  type: "study_guide";
  version: string;
  modules: StudyGuideModule[];
}

export interface BriefingSection {
  heading: string;
  content_md?: string;
  items?: string[];
}

export interface BriefingPayload {
  type: "briefing_doc";
  version: string;
  sections: BriefingSection[];
}

export interface TimelineEvent {
  date: string;
  title: string;
  summary_md: string;
  source_urls: string[];
}

export interface TimelinePayload {
  type: "timeline";
  version: string;
  events: TimelineEvent[];
}

export interface MindMapNode {
  id: string;
  label: string;
  children: MindMapNode[];
}

export interface MindMapPayload {
  type: "mind_map";
  version: string;
  nodes: MindMapNode[];
}

export type StructuredPayload = 
  | FAQPayload 
  | StudyGuidePayload 
  | BriefingPayload 
  | TimelinePayload 
  | MindMapPayload;

export interface DiscoverRecommendation {
  title: string;
  url: string;
  why_md: string;
  summary_md: string;
  published?: string;
  score: number;
}

export interface DiscoverResponse {
  recommendations: DiscoverRecommendation[];
  queries_planned: string[];
  diagnostics: {
    searchProvider?: string;
    llm?: string;
    latencyMs?: number;
    cached: boolean;
  };
}