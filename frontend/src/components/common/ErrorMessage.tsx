import React from 'react';
import { AlertCircle } from 'lucide-react';

interface ErrorMessageProps {
  title?: string;
  message: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ title = 'Error', message }) => {
  return (
    <div className="max-w-2xl mx-auto w-full p-6 bg-destructive/10 border border-destructive/20 rounded-2xl flex items-start gap-4">
      <AlertCircle className="w-6 h-6 text-destructive shrink-0 mt-0.5" />
      <div className="space-y-1">
        <h4 className="font-bold text-destructive">{title}</h4>
        <p className="text-sm text-destructive/80 leading-relaxed">{message}</p>
      </div>
    </div>
  );
};

export default ErrorMessage;
