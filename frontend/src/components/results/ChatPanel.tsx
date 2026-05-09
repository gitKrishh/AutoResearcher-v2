import React, { useState } from 'react';
import { Send, Loader2, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiService } from '@/services/apiService';
import { toast } from 'sonner';

const ChatPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMsg = query.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await apiService.chat(userMsg);
      if (response.success && response.data) {
        setMessages(prev => [...prev, { role: 'assistant', content: response.data!.answer }]);
      } else {
        toast.error(response.error?.message || 'Failed to get answer');
      }
    } catch (err: any) {
      toast.error(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-card border border-border rounded-3xl overflow-hidden flex flex-col h-[500px]">
      <div className="p-4 border-b border-border bg-card/50 flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-primary" />
        <h3 className="font-bold">Ask follow-up questions</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-2 opacity-50">
            <MessageSquare className="w-8 h-8" />
            <p className="text-sm">Ask about specific methodologies, findings, or datasets mentioned in the papers.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-primary text-primary-foreground rounded-tr-none' 
                : 'bg-muted border border-border rounded-tl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted border border-border p-4 rounded-2xl rounded-tl-none flex gap-2 items-center text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              AI is thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="p-4 border-t border-border bg-card/50 flex gap-2">
        <Input 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          className="flex-1 rounded-full border-border bg-background"
        />
        <Button type="submit" disabled={isLoading || !query.trim()} size="icon" className="rounded-full shrink-0">
          <Send className="w-4 h-4" />
        </Button>
      </form>
    </div>
  );
};

export default ChatPanel;
