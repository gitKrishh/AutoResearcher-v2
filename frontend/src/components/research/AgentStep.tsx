import React from 'react';
import { CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { PipelineStep } from '@/hooks/useResearch';

interface AgentStepProps {
  name: string;
  description: string;
  status: 'pending' | 'active' | 'done' | 'error';
}

const AgentStep: React.FC<AgentStepProps> = ({ name, description, status }) => {
  return (
    <div className={cn(
      "flex items-start gap-4 p-4 rounded-2xl border transition-all duration-300",
      status === 'active' ? "bg-primary/5 border-primary/30 shadow-lg shadow-primary/5 scale-[1.02]" : "bg-card/50 border-border opacity-60"
    )}>
      <div className="mt-1">
        {status === 'pending' && <Circle className="w-5 h-5 text-muted-foreground" />}
        {status === 'active' && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
        {status === 'done' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
        {status === 'error' && <AlertCircle className="w-5 h-5 text-destructive" />}
      </div>
      
      <div className="space-y-1">
        <h4 className={cn(
          "font-bold",
          status === 'active' ? "text-primary" : "text-foreground"
        )}>
          {name}
        </h4>
        <p className="text-xs text-muted-foreground leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
};

export default AgentStep;
