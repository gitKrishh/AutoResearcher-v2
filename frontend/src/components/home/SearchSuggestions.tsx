import React from 'react';
import { Sparkles } from 'lucide-react';

interface SearchSuggestionsProps {
  onSelect: (suggestion: string) => void;
}

const SUGGESTIONS = [
  "Transformer attention mechanism optimization",
  "LLM Hallucination mitigation techniques",
  "Autonomous AI Agent architectures",
  "Retrieval Augmented Generation best practices",
];

const SearchSuggestions: React.FC<SearchSuggestionsProps> = ({ onSelect }) => {
  return (
    <div className="flex flex-col items-center gap-4 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Sparkles className="w-4 h-4 text-primary" />
        <span>Try searching for</span>
      </div>
      <div className="flex flex-wrap justify-center gap-2 max-w-2xl">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSelect(suggestion)}
            className="px-4 py-2 bg-card/50 hover:bg-card border border-border rounded-full text-sm font-medium transition-all hover:border-primary/40 hover:text-primary"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SearchSuggestions;
