import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const useSearch = () => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    // Navigate to research page with the query
    navigate(`/research?q=${encodeURIComponent(query.trim())}`);
  };

  const setSuggestion = (suggestion: string) => {
    setQuery(suggestion);
  };

  return {
    query,
    setQuery,
    handleSearch,
    setSuggestion,
  };
};
