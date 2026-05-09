import React from 'react';
import { SearchX } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  message: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({ title, message }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center space-y-4">
      <div className="p-4 bg-muted rounded-full">
        <SearchX className="w-12 h-12 text-muted-foreground" />
      </div>
      <div className="space-y-1">
        <h3 className="text-xl font-bold">{title}</h3>
        <p className="text-muted-foreground max-w-sm">{message}</p>
      </div>
    </div>
  );
};

export default EmptyState;
