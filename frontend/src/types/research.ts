import type { PaperAnalysis } from './paper';

export interface InsightReport {
  research_gaps: string[];
  contradictions: string[];
  trends: string[];
  future_directions: string[];
}

export interface FinalReport {
  topic: string;
  paper_count: number;
  papers: PaperAnalysis[];
  literature_review: string;
  insights: InsightReport | null;
  generated_at: string;
}

export interface ResearchRequest {
  topic: string;
  max_papers?: number;
  include_insights?: boolean;
}
