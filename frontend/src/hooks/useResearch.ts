import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { apiService } from '@/services/apiService';
import { FinalReport } from '@/types/research';
import { toast } from 'sonner';

export type PipelineStep = 
  | 'idle'
  | 'planning'
  | 'searching'
  | 'processing'
  | 'vectorizing'
  | 'analyzing'
  | 'synthesizing'
  | 'writing'
  | 'complete'
  | 'error';

export const useResearch = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const query = searchParams.get('q');
  
  const [currentStep, setCurrentStep] = useState<PipelineStep>('idle');
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<FinalReport | null>(null);

  const conductResearch = useCallback(async (topic: string) => {
    setCurrentStep('planning');
    setError(null);

    // Simulate step transitions since we don't have streaming yet
    const steps: PipelineStep[] = [
      'planning', 'searching', 'processing', 'vectorizing', 'analyzing', 'synthesizing', 'writing'
    ];
    
    let stepIdx = 0;
    const interval = setInterval(() => {
      if (stepIdx < steps.length - 1) {
        stepIdx++;
        setCurrentStep(steps[stepIdx]);
      } else {
        clearInterval(interval);
      }
    }, 4000); // Change step every 4s for visual feedback

    try {
      const response = await apiService.conductResearch({
        topic,
        max_papers: 5,
        include_insights: true
      });

      clearInterval(interval);

      if (response.success && response.data) {
        setCurrentStep('complete');
        setReport(response.data);
        // Save to global state or navigate to results
        // For now, we'll just navigate to results page
        // and pass the report data via session storage or state
        sessionStorage.setItem('last_report', JSON.stringify(response.data));
        navigate('/results');
      } else {
        setCurrentStep('error');
        setError(response.error?.message || 'Research pipeline failed.');
        toast.error(response.error?.message || 'Research pipeline failed.');
      }
    } catch (err: any) {
      clearInterval(interval);
      setCurrentStep('error');
      const msg = err.response?.data?.error?.message || err.message || 'An unexpected error occurred.';
      setError(msg);
      toast.error(msg);
    }
  }, [navigate]);

  useEffect(() => {
    if (query && currentStep === 'idle') {
      conductResearch(query);
    }
  }, [query, currentStep, conductResearch]);

  return {
    query,
    currentStep,
    error,
    report,
    retry: () => query && conductResearch(query)
  };
};
