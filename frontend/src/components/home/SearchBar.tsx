import React from 'react';
import { Search, ArrowRight } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface SearchBarProps {
  query: string;
  setQuery: (query: string) => void;
  onSearch: (e: React.FormEvent) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ query, setQuery, onSearch }) => {
  return (
    <form 
      onSubmit={onSearch} 
      className="relative max-w-2xl mx-auto w-full group"
    >
      <div className="absolute inset-0 bg-primary/20 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="relative flex items-center bg-card border border-border rounded-full p-2 shadow-2xl overflow-hidden focus-within:border-primary/50 transition-all duration-300">
        <Search className="w-5 h-5 text-muted-foreground ml-4" />
        <Input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What would you like to research today?"
          className="flex-1 bg-transparent border-none outline-none focus-visible:ring-0 px-4 py-6 text-lg placeholder:text-muted-foreground/60"
        />
        <Button
          type="submit"
          disabled={!query.trim()}
          className="rounded-full px-8 py-6 h-auto font-bold transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
        >
          Research
          <ArrowRight className="w-5 h-5" />
        </Button>
      </div>
    </form>
  );
};

export default SearchBar;
