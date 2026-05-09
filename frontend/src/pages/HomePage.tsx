import React from 'react';
import SearchBar from '@/components/home/SearchBar';
import SearchSuggestions from '@/components/home/SearchSuggestions';
import { useSearch } from '@/hooks/useSearch';
import { Sparkles, Zap, Shield, BarChart3 } from 'lucide-react';

const HomePage: React.FC = () => {
  const { query, setQuery, handleSearch, setSuggestion } = useSearch();

  return (
    <div className="flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full py-20 md:py-32 px-4 flex flex-col items-center text-center space-y-8 relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-primary/10 blur-[120px] rounded-full -z-10 opacity-50" />
        
        <div className="space-y-4 animate-in fade-in slide-in-from-top-8 duration-1000">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-xs font-bold text-primary tracking-wider uppercase mb-4">
            <Sparkles className="w-3 h-3" />
            AI-Powered Research
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-[1.1]">
            Your Autonomous <span className="text-primary">Academic Assistant</span>
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
            Search thousands of papers, extract key findings, and generate a comprehensive literature review in seconds.
          </p>
        </div>

        <div className="w-full max-w-3xl pt-8 animate-in fade-in zoom-in duration-1000 delay-200">
          <SearchBar 
            query={query} 
            setQuery={setQuery} 
            onSearch={handleSearch} 
          />
        </div>

        <SearchSuggestions onSelect={setSuggestion} />
      </section>

      {/* Features Section */}
      <section className="w-full max-w-7xl px-4 py-24 grid md:grid-cols-3 gap-8 border-t border-border/50">
        <div className="bg-card/50 border border-border p-8 rounded-3xl space-y-4 hover:border-primary/30 transition-colors group">
          <div className="p-3 bg-primary/10 rounded-2xl w-fit group-hover:bg-primary/20 transition-colors">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <h3 className="text-xl font-bold">Rapid Synthesis</h3>
          <p className="text-muted-foreground leading-relaxed">
            Our multi-agent system reads and compares multiple papers simultaneously to give you the big picture instantly.
          </p>
        </div>

        <div className="bg-card/50 border border-border p-8 rounded-3xl space-y-4 hover:border-primary/30 transition-colors group">
          <div className="p-3 bg-primary/10 rounded-2xl w-fit group-hover:bg-primary/20 transition-colors">
            <BarChart3 className="w-6 h-6 text-primary" />
          </div>
          <h3 className="text-xl font-bold">Deep Insights</h3>
          <p className="text-muted-foreground leading-relaxed">
            Automatically identifies research gaps, contradictions, and future trends that are often missed in manual reviews.
          </p>
        </div>

        <div className="bg-card/50 border border-border p-8 rounded-3xl space-y-4 hover:border-primary/30 transition-colors group">
          <div className="p-3 bg-primary/10 rounded-2xl w-fit group-hover:bg-primary/20 transition-colors">
            <Shield className="w-6 h-6 text-primary" />
          </div>
          <h3 className="text-xl font-bold">Citations Included</h3>
          <p className="text-muted-foreground leading-relaxed">
            Every claim in the generated literature review is grounded in actual research with links back to the original PDFs.
          </p>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
