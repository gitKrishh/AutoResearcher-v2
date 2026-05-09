import React from 'react';
import { PaperAnalysis } from '@/types/paper';
import { ExternalLink, FileText, Calendar, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface PaperListProps {
  papers: PaperAnalysis[];
}

const PaperList: React.FC<PaperListProps> = ({ papers }) => {
  return (
    <div className="grid gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {papers.map((paper) => (
        <div 
          key={paper.id}
          className="bg-card border border-border rounded-3xl p-6 hover:border-primary/30 transition-all hover:shadow-xl hover:shadow-primary/5 group"
        >
          <div className="flex flex-col md:flex-row justify-between items-start gap-4 mb-6">
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20">
                  {paper.source}
                </Badge>
                <Badge variant="outline" className="flex gap-1 items-center">
                  <Calendar className="w-3 h-3" />
                  {paper.published}
                </Badge>
              </div>
              <h3 className="text-2xl font-bold group-hover:text-primary transition-colors leading-tight">
                {paper.title}
              </h3>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="w-4 h-4" />
                <span>{paper.authors.join(', ')}</span>
              </div>
            </div>
            
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 px-5 py-2.5 bg-primary/10 text-primary hover:bg-primary/20 rounded-full text-sm font-bold transition-all shrink-0"
            >
              <ExternalLink className="w-4 h-4" />
              View PDF
            </a>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-3">
              <div className="flex items-center gap-2 font-bold text-sm text-primary uppercase tracking-wider">
                <FileText className="w-4 h-4" />
                AI Summary
              </div>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {paper.summary}
              </p>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2 font-bold text-sm text-primary uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                Key Findings
              </div>
              <p className="text-muted-foreground text-sm leading-relaxed">
                {paper.key_findings}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PaperList;
