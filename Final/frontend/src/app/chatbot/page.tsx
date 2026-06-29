// ====================================================================
// RADIX Placement Chatbot Page component (Next.js)
// Place in: Final/frontend/src/app/chatbot/page.tsx
// ====================================================================

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { Layout } from '@/components';
import { fetchApi } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
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
    <Layout>
      <div className="flex flex-col h-[calc(100vh-80px)] max-w-5xl mx-auto p-4 sm:p-6 font-sans">
        {/* Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-slate-200 mb-4">
          <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 border border-blue-100">
            <Bot className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Placement Chatbot</h1>
            <p className="text-xs text-slate-500">Semantic Intelligence & RAG Chat Layer</p>
          </div>
        </div>

        {/* Preset Queries */}
        {messages.length === 1 && (
          <div className="mb-6 animate-fade-in">
            <p className="text-sm font-medium text-slate-500 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-500" /> Suggested Queries:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {presets.map((preset, index) => (
                <button
                  key={index}
                  onClick={() => handleSend(preset)}
                  className="text-left px-4 py-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-sm transition-all duration-200 hover:border-blue-300 hover:shadow-sm"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto bg-white rounded-2xl border border-slate-200 p-4 mb-4 space-y-4 shadow-inner scrollbar-thin">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 max-w-[85%] ${
                msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-semibold border ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-slate-100 text-slate-600 border-slate-200'
                }`}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className="flex flex-col gap-1">
                <div
                  className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-slate-50 text-slate-800 rounded-tl-none border border-slate-100'
                  }`}
                >
                  {msg.content}
                </div>

                {/* RAG Citations */}
                {msg.role === 'assistant' && msg.context && msg.context.length > 0 && (
                  <div className="text-[10px] text-slate-500 flex items-center gap-1.5 mt-1 px-1">
                    <span className="font-semibold uppercase tracking-wider">Semantic Sources:</span>
                    {msg.context.map((source, sIdx) => (
                      <span
                        key={sIdx}
                        className="bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded text-[10px] text-slate-700 font-medium"
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
              <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 text-slate-600 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 animate-bounce" />
              </div>
              <div className="bg-slate-50 text-slate-500 border border-slate-100 rounded-2xl rounded-tl-none px-4 py-2.5 text-sm flex items-center gap-1">
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100" />
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200" />
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-300" />
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
            placeholder="Ask placement chatbot about company metrics, similarities, growth projections..."
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-5 rounded-xl flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </Layout>
  );
}
