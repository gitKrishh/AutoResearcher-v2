import React from 'react';
import AgentStep from './AgentStep';
import { PipelineStep } from '@/hooks/useResearch';

interface PipelineTrackerProps {
  currentStep: PipelineStep;
}

const STEPS = [
  { id: 'planning', name: 'Planner Agent', description: 'Decomposing research topic into sub-queries' },
  { id: 'searching', name: 'Search Agent', description: 'Retrieving relevant papers from arXiv' },
  { id: 'processing', name: 'PDF Agent', description: 'Downloading and extracting text from PDFs' },
  { id: 'vectorizing', name: 'Embedding Agent', description: 'Generating vectors and storing in FAISS' },
  { id: 'analyzing', name: 'Analysis Agent', description: 'Extracting key findings from each paper' },
  { id: 'synthesizing', name: 'Insight Agent', description: 'Comparing findings and identifying gaps' },
  { id: 'writing', name: 'Writer Agent', description: 'Compiling final literature review report' },
];

const PipelineTracker: React.FC<PipelineTrackerProps> = ({ currentStep }) => {
  const getStatus = (stepId: string) => {
    if (currentStep === 'error') return 'error';
    if (currentStep === 'complete') return 'done';
    
    const currentIndex = STEPS.findIndex(s => s.id === currentStep);
    const stepIndex = STEPS.findIndex(s => s.id === stepId);
    
    if (stepIndex < currentIndex) return 'done';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="grid gap-3 w-full max-w-md mx-auto">
      {STEPS.map((step) => (
        <AgentStep 
          key={step.id}
          name={step.name}
          description={step.description}
          status={getStatus(step.id)}
        />
      ))}
    </div>
  );
};

export default PipelineTracker;
