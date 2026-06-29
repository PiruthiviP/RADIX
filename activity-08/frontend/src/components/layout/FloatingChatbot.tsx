// ====================================================================
// RADIX Global Floating Copilot Chatbot Widget
// Place in: activity-08/frontend/src/components/layout/FloatingChatbot.tsx
// ====================================================================

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { 
  MessageSquare, 
  X, 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  ChevronDown,
  Minimize2
} from 'lucide-react';
import { fetchApi } from '@/lib/api';
import { cn } from '@/lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  context?: string[];
}

export const FloatingChatbot: React.FC = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I am your placement chatbot. How can I help you today?",
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, loading, isOpen]);

  // Only render for authenticated Students and Admins
  const role = user?.role || 'Guest';
  if (role !== 'Student' && role !== 'Admin') {
    return null;
  }

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Keep last 10 messages for conversational context
      const chatHistory = messages.slice(-10).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const res = await fetchApi('/api/chatbot', {
        method: 'POST',
        body: JSON.stringify({
          messages: [...chatHistory, { role: 'user', content: text }],
          prompt: text,
        }),
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.response,
          context: res.context,
        },
      ]);
    } catch (err: any) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Connection failed: Make sure your RADIX FastAPI server is running on port 8000.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Floating Chat Bubble Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={cn(
            "w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300",
            "bg-primary hover:bg-primary/90 text-primary-foreground hover:scale-110",
            "relative group active:scale-95"
          )}
        >
          <MessageSquare className="w-6 h-6 animate-pulse" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-rose-500 rounded-full border-2 border-background animate-ping"></div>
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-rose-500 rounded-full border-2 border-background"></div>
        </button>
      )}

      {/* Floating Chat Panel Drawer */}
      {isOpen && (
        <div 
          className={cn(
            "w-96 h-[500px] rounded-2xl border border-border bg-card/95 backdrop-blur-md shadow-2xl flex flex-col overflow-hidden",
            "animate-in slide-in-from-bottom-5 fade-in duration-300"
          )}
        >
          {/* Header Panel */}
          <div className="bg-gradient-to-r from-sidebar-primary to-indigo-600 p-4 text-primary-foreground flex items-center justify-between shadow-md">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                <Bot className="w-4.5 h-4.5 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold leading-none font-display">Placement Chatbot</h3>
                <span className="text-[10px] text-white/70 leading-none">RADIX Assistant</span>
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-white/80 hover:text-white transition-colors"
                title="Minimize"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/10 text-white/80 hover:text-white transition-colors"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Logs Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
            {messages.map((msg, index) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={index}
                  className={cn("flex gap-2 max-w-[85%] animate-in fade-in slide-in-from-bottom-1 duration-200", isUser ? "ml-auto flex-row-reverse" : "")}
                >
                  <div
                    className={cn(
                      "w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-semibold border",
                      isUser 
                        ? "bg-primary text-primary-foreground border-primary" 
                        : "bg-muted text-muted-foreground border-border"
                    )}
                  >
                    {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                  </div>

                  <div className="flex flex-col gap-1">
                    <div
                      className={cn(
                        "px-3 py-2 rounded-xl text-xs leading-relaxed whitespace-pre-wrap shadow-sm",
                        isUser 
                          ? "bg-primary text-primary-foreground rounded-tr-none" 
                          : "bg-accent/40 text-foreground rounded-tl-none border border-border/40"
                      )}
                    >
                      {msg.content}
                    </div>

                    {/* Citations references */}
                    {!isUser && msg.context && msg.context.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-0.5 px-0.5">
                        {msg.context.map((source, sIdx) => (
                          <span 
                            key={sIdx} 
                            className="bg-accent/80 border border-border/80 text-[8px] font-semibold text-foreground px-1 py-0.5 rounded"
                          >
                            {source}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Waiting loading state */}
            {loading && (
              <div className="flex gap-2 max-w-[80%]">
                <div className="w-7 h-7 rounded-lg bg-muted border border-border flex items-center justify-center flex-shrink-0">
                  <Bot className="w-3.5 h-3.5 animate-bounce" />
                </div>
                <div className="bg-accent/40 border border-border/40 rounded-xl rounded-tl-none px-3 py-2 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-foreground/60 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-foreground/60 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 bg-foreground/60 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Footer Input Area */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="p-3 border-t border-border/60 bg-muted/30 flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot..."
              className="flex-1 bg-[#14151b] border border-border hover:border-border/100 focus:border-primary/50 text-slate-100 px-3 py-2 rounded-xl text-xs focus:outline-none transition-all duration-300 placeholder:text-muted-foreground/60"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-primary text-primary-foreground w-8 h-8 rounded-xl flex items-center justify-center hover:bg-primary/95 disabled:opacity-50 transition-colors shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
export default FloatingChatbot;
