import { useState } from 'react';
import axios from 'axios';
import { Search, Loader2, BookOpen, ExternalLink, ArrowRight, Sparkles, Database, FileText } from 'lucide-react';

interface PaperAnalysis {
  id: string;
  title: string;
  abstract: string;
  authors: string[];
  pdf_url: string;
  published: string;
  source: string;
  summary: string;
  methodology: string;
  key_findings: string;
}

interface InsightReport {
  research_gaps: string[];
  contradictions: string[];
  trends: string[];
  future_directions: string[];
}

interface FinalReport {
  topic: string;
  paper_count: number;
  papers: PaperAnalysis[];
  literature_review: string;
  insights: InsightReport | null;
  generated_at: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [researchData, setResearchData] = useState<FinalReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResearchData(null);

    try {
      const response = await axios.post('http://localhost:8000/api/research', {
        topic: query.trim(),
        max_papers: 3, // keep it small for faster MVP testing
        include_insights: true,
      });

      if (response.data.success) {
        setResearchData(response.data.data);
      } else {
        setError(response.data.error?.message || 'Research failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col p-8 max-w-5xl mx-auto">
      <header className="py-12 flex flex-col items-center text-center space-y-4">
        <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-2xl mb-2">
          <BookOpen className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">AutoResearcher</h1>
        <p className="text-muted text-lg max-w-xl">
          Search, analyze, and review academic papers autonomously. Powered by AI.
        </p>
      </header>

      <main className="flex-1 w-full space-y-12">
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto w-full relative group">
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <div className="relative flex items-center bg-card border border-cardBorder rounded-full p-2 shadow-2xl overflow-hidden focus-within:border-primary/50 transition-colors">
            <Search className="w-5 h-5 text-muted ml-4" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Conduct full research on a topic (e.g. LLM Agents)..."
              className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-foreground placeholder:text-muted"
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="bg-primary hover:bg-primaryHover text-white px-6 py-3 rounded-full font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Researching...
                </>
              ) : (
                <>
                  Research
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
          {isLoading && (
            <p className="text-center text-sm text-primary/80 mt-4 animate-pulse">
              Planning → Searching → Downloading → Vectorizing → Deep Analysis → Synthesizing Insights → Writing Report... (Takes ~30-60s)
            </p>
          )}
        </form>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-center max-w-2xl mx-auto">
            {error}
          </div>
        )}

        {researchData && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
            {/* Literature Review Section */}
            <div className="bg-card border border-primary/30 rounded-3xl p-8 shadow-2xl shadow-primary/5 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-primary" />
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-primary/20 rounded-lg">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <h2 className="text-2xl font-bold">Final Literature Review</h2>
              </div>
              
              <div className="prose prose-invert prose-primary max-w-none">
                {/* Very simple markdown parsing for MVP */}
                {researchData.literature_review.split('\n').map((para, i) => {
                  if (para.startsWith('# ')) return <h1 key={i} className="text-3xl font-bold mt-8 mb-4">{para.replace('# ', '')}</h1>;
                  if (para.startsWith('## ')) return <h2 key={i} className="text-2xl font-semibold mt-6 mb-3">{para.replace('## ', '')}</h2>;
                  if (para.startsWith('### ')) return <h3 key={i} className="text-xl font-medium mt-4 mb-2">{para.replace('### ', '')}</h3>;
                  if (para.trim() === '') return <br key={i} />;
                  return <p key={i} className="text-foreground/90 leading-relaxed text-lg mb-4">{para}</p>;
                })}
              </div>

              <div className="flex flex-wrap gap-4 mt-8 pt-6 border-t border-cardBorder">
                <div className="flex items-center gap-2 text-sm text-muted bg-background px-4 py-2 rounded-full border border-cardBorder">
                  <FileText className="w-4 h-4 text-primary" />
                  {researchData.paper_count} Papers Processed
                </div>
              </div>
            </div>

            {/* Insights Section */}
            {researchData.insights && (
              <div className="grid md:grid-cols-2 gap-6">
                 <div className="bg-card border border-cardBorder rounded-2xl p-6">
                   <h3 className="text-xl font-semibold mb-4 text-yellow-400">Research Gaps</h3>
                   <ul className="list-disc pl-5 space-y-2 text-muted">
                     {researchData.insights.research_gaps.map((gap, i) => <li key={i}>{gap}</li>)}
                   </ul>
                 </div>
                 <div className="bg-card border border-cardBorder rounded-2xl p-6">
                   <h3 className="text-xl font-semibold mb-4 text-blue-400">Future Directions</h3>
                   <ul className="list-disc pl-5 space-y-2 text-muted">
                     {researchData.insights.future_directions.map((dir, i) => <li key={i}>{dir}</li>)}
                   </ul>
                 </div>
              </div>
            )}

            {/* Sources Section */}
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-cardBorder pb-4">
                <h2 className="text-2xl font-semibold">Source Papers</h2>
              </div>

              <div className="grid gap-6">
                {researchData.papers.map((paper) => (
                  <div
                    key={paper.id}
                    className="bg-card border border-cardBorder rounded-2xl p-6 hover:border-primary/30 transition-all hover:shadow-lg hover:shadow-primary/5 group"
                  >
                    <div className="flex justify-between items-start gap-4">
                      <div className="space-y-2">
                        <h3 className="text-xl font-semibold leading-tight group-hover:text-primary transition-colors">
                          {paper.title}
                        </h3>
                        <p className="text-sm text-primary/80 font-medium">
                          {paper.authors.join(', ')} • {paper.published}
                        </p>
                      </div>
                      <a
                        href={paper.pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-sm bg-primary/10 text-primary hover:bg-primary/20 px-4 py-2 rounded-lg font-medium transition-colors shrink-0"
                      >
                        <ExternalLink className="w-4 h-4" />
                        PDF
                      </a>
                    </div>
                    <div className="mt-4 pt-4 border-t border-cardBorder">
                      <p className="text-sm font-semibold text-primary mb-1">AI Summary:</p>
                      <p className="text-muted leading-relaxed text-sm">
                        {paper.summary}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
