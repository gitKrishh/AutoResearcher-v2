import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ReportViewProps {
  content: string;
}

const ReportView: React.FC<ReportViewProps> = ({ content }) => {
  return (
    <div className="bg-card border border-border rounded-3xl p-8 md:p-12 shadow-sm animate-in fade-in duration-700">
      <article className="prose prose-invert prose-primary max-w-none prose-headings:font-bold prose-h1:text-4xl prose-h2:text-2xl prose-p:text-foreground/90 prose-p:leading-relaxed prose-li:text-foreground/80">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </article>
    </div>
  );
};

export default ReportView;
