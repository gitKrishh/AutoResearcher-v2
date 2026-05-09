import React from 'react';
import PipelineTracker from '@/components/research/PipelineTracker';
import { useResearch } from '@/hooks/useResearch';
import ErrorMessage from '@/components/common/ErrorMessage';
import { Button } from '@/components/ui/button';
import { RotateCcw, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

const ResearchPage: React.FC = () => {
  const { query, currentStep, error, retry } = useResearch();

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 space-y-12">
      <header className="text-center space-y-4">
        <h2 className="text-3xl font-bold tracking-tight">Researching</h2>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-muted rounded-full border border-border">
          <span className="text-sm font-medium text-muted-foreground italic">"{query}"</span>
        </div>
      </header>

      <div className="flex flex-col items-center gap-8">
        {currentStep !== 'error' && (
          <div className="w-full space-y-8 animate-in fade-in duration-500">
             <PipelineTracker currentStep={currentStep} />
          </div>
        )}

        {currentStep === 'error' && (
          <div className="w-full space-y-6 animate-in zoom-in duration-300">
            <ErrorMessage title="Research Pipeline Failed" message={error || 'An unknown error occurred.'} />
            <div className="flex justify-center gap-4">
              <Button onClick={retry} variant="outline" className="gap-2">
                <RotateCcw className="w-4 h-4" />
                Try Again
              </Button>
              <Button asChild className="gap-2">
                <Link to="/">
                  <Home className="w-4 h-4" />
                  Back to Home
                </Link>
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchPage;
