import React from 'react';
import type { InsightReport } from '@/types/research';
import { Lightbulb, Target, TrendingUp, Compass } from 'lucide-react';

interface InsightPanelProps {
  insights: InsightReport;
}

const InsightPanel: React.FC<InsightPanelProps> = ({ insights }) => {
  return (
    <div className="grid md:grid-cols-2 gap-6 animate-in fade-in duration-500">
      <InsightCard 
        title="Research Gaps" 
        items={insights.research_gaps} 
        icon={<Target className="w-5 h-5" />}
        color="text-yellow-500"
        bgColor="bg-yellow-500/10"
      />
      <InsightCard 
        title="Trends" 
        items={insights.trends} 
        icon={<TrendingUp className="w-5 h-5" />}
        color="text-blue-500"
        bgColor="bg-blue-500/10"
      />
      <InsightCard 
        title="Contradictions" 
        items={insights.contradictions} 
        icon={<Lightbulb className="w-5 h-5" />}
        color="text-red-500"
        bgColor="bg-red-500/10"
      />
      <InsightCard 
        title="Future Directions" 
        items={insights.future_directions} 
        icon={<Compass className="w-5 h-5" />}
        color="text-green-500"
        bgColor="bg-green-500/10"
      />
    </div>
  );
};

interface InsightCardProps {
  title: string;
  items: string[];
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

const InsightCard: React.FC<InsightCardProps> = ({ title, items, icon, color, bgColor }) => (
  <div className="bg-card border border-border rounded-3xl p-6 space-y-4">
    <div className="flex items-center gap-3">
      <div className={`p-2 ${bgColor} rounded-xl ${color}`}>
        {icon}
      </div>
      <h4 className="font-bold text-lg">{title}</h4>
    </div>
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-3 text-sm text-muted-foreground leading-relaxed">
          <div className={`w-1.5 h-1.5 rounded-full ${color} mt-1.5 shrink-0`} />
          {item}
        </li>
      ))}
      {items.length === 0 && (
        <li className="text-sm text-muted-foreground italic">No specific insights identified.</li>
      )}
    </ul>
  </div>
);

export default InsightPanel;
