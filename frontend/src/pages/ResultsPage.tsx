import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FinalReport } from '@/types/research';
import ReportView from '@/components/results/ReportView';
import PaperList from '@/components/results/PaperList';
import InsightPanel from '@/components/results/InsightPanel';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { FileText, Sparkles, BookOpen, ArrowLeft, Download, Share2 } from 'lucide-react';

const ResultsPage: React.FC = () => {
  const [report, setReport] = useState<FinalReport | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const savedReport = sessionStorage.getItem('last_report');
    if (savedReport) {
      setReport(JSON.parse(savedReport));
    } else {
      navigate('/');
    }
  }, [navigate]);

  if (!report) return null;

  return (
    <div className="max-w-6xl mx-auto py-12 px-4 space-y-12 animate-in fade-in duration-500">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-4">
          <Button 
            variant="ghost" 
            className="p-0 h-auto hover:bg-transparent hover:text-primary transition-colors gap-2 text-muted-foreground"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Search
          </Button>
          <div className="space-y-1">
            <h1 className="text-4xl font-extrabold tracking-tight leading-tight">
              Research Report: <span className="text-primary">{report.topic}</span>
            </h1>
            <p className="text-muted-foreground">
              Synthesized from {report.paper_count} peer-reviewed sources • {new Date(report.generated_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" className="gap-2 rounded-full px-6">
            <Share2 className="w-4 h-4" />
            Share
          </Button>
          <Button className="gap-2 rounded-full px-6 bg-primary hover:bg-primaryHover">
            <Download className="w-4 h-4" />
            Export PDF
          </Button>
        </div>
      </header>

      <Tabs defaultValue="report" className="w-full space-y-8">
        <div className="flex justify-center border-b border-border pb-px">
          <TabsList className="bg-transparent h-auto p-0 gap-8">
            <TabsTrigger 
              value="report" 
              className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 py-4 font-bold text-base transition-all"
            >
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Literature Review
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="insights" 
              className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 py-4 font-bold text-base transition-all"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Deep Insights
              </div>
            </TabsTrigger>
            <TabsTrigger 
              value="papers" 
              className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:text-primary data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 py-4 font-bold text-base transition-all"
            >
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                Analyzed Papers
              </div>
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="report" className="mt-0 ring-offset-transparent focus-visible:ring-0">
          <ReportView content={report.literature_review} />
        </TabsContent>

        <TabsContent value="insights" className="mt-0 ring-offset-transparent focus-visible:ring-0">
          {report.insights ? (
            <InsightPanel insights={report.insights} />
          ) : (
            <div className="text-center py-20 text-muted-foreground italic">
              No cross-paper insights were generated for this report.
            </div>
          )}
        </TabsContent>

        <TabsContent value="papers" className="mt-0 ring-offset-transparent focus-visible:ring-0">
          <PaperList papers={report.papers} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ResultsPage;
