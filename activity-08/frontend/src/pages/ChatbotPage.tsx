import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, MessageCircle, RefreshCw } from 'lucide-react';
import { fetchApi } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: str;
  context?: string[];
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I am your placement chatbot. How can I help you today?",
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const presets = [
    "Which companies are similar to Concentrix?",
    "Show me Fintech companies with High AI adoption.",
    "Give me strategic recommendations for Llama Logisol.",
    "Which companies show similar innovation patterns to DevRev?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;
    
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Clean history for API payload (limit history to last 10 messages to avoid large payloads)
      const chatHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const res = await fetchApi('/api/chatbot', {
        method: 'POST',
        body: JSON.stringify({
          messages: [...chatHistory, { role: 'user', content: text }],
          prompt: text
        })
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.response,
        context: res.context
      }]);
    } catch (err: any) {
      console.error(err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: Unable to reach the conversational AI server (${err.message || 'Connection failed'}). Please verify that the backend container is running on port 8000.`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] max-w-5xl mx-auto p-4 font-sans">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-border mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
          <Bot className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Placement Chatbot</h1>
          <p className="text-xs text-muted-foreground">Semantic Intelligence & RAG Chat Layer</p>
        </div>
      </div>

      {/* Preset Queries */}
      {messages.length === 1 && (
        <div className="mb-6 animate-fade-in">
          <p className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" /> Suggested Queries:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {presets.map((preset, index) => (
              <button
                key={index}
                onClick={() => handleSend(preset)}
                className="text-left px-4 py-3 rounded-xl border border-border bg-card hover:bg-accent/40 text-sm transition-all duration-200 hover:border-primary/40 shadow-sm"
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto bg-card rounded-2xl border border-border p-4 mb-4 space-y-4 scrollbar-thin shadow-inner">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-3 max-w-[85%] ${
              msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-semibold ${
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-accent text-accent-foreground'
              }`}
            >
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Message Bubble */}
            <div className="flex flex-col gap-1">
              <div
                className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none'
                    : 'bg-accent/50 text-foreground rounded-tl-none'
                }`}
              >
                {msg.content}
              </div>

              {/* RAG Citations */}
              {msg.role === 'assistant' && msg.context && msg.context.length > 0 && (
                <div className="text-[10px] text-muted-foreground flex items-center gap-1.5 mt-1 px-1">
                  <span className="font-semibold uppercase tracking-wider">Semantic Sources:</span>
                  {msg.context.map((source, sIdx) => (
                    <span
                      key={sIdx}
                      className="bg-accent/80 border border-border/80 px-1.5 py-0.5 rounded text-[10px] text-foreground font-medium"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 max-w-[80%]">
            <div className="w-8 h-8 rounded-lg bg-accent text-accent-foreground flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 animate-bounce" />
            </div>
            <div className="bg-accent/50 text-foreground rounded-2xl rounded-tl-none px-4 py-3 text-sm flex items-center gap-1">
              <span className="w-2 h-2 bg-foreground/60 rounded-full animate-bounce delay-100" />
              <span className="w-2 h-2 bg-foreground/60 rounded-full animate-bounce delay-200" />
              <span className="w-2 h-2 bg-foreground/60 rounded-full animate-bounce delay-300" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend(input);
        }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Antigravity about company metrics, similarities, clusters..."
          className="flex-1 px-4 py-3 rounded-xl border border-border bg-card text-slate-100 placeholder:text-muted-foreground/60 text-sm focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-primary text-primary-foreground px-4 rounded-xl flex items-center justify-center hover:bg-primary/95 disabled:opacity-50 transition-colors shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
