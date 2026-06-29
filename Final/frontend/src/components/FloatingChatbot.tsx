// ====================================================================
// RADIX Next.js Global Floating Placements Chatbot Widget
// Place in: Final/frontend/src/components/FloatingChatbot.tsx
// ====================================================================

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, 
  X, 
  Send, 
  Bot, 
  User, 
  Minimize2
} from 'lucide-react';
import { fetchApi } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  context?: string[];
}

export const FloatingChatbot: React.FC = () => {
  const [role, setRole] = useState<string>('Guest');
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

  // Fetch session on mount
  useEffect(() => {
    let isMounted = true;
    fetch('/api/auth/session')
      .then(res => res.json())
      .then(data => {
        if (isMounted && data.authenticated && data.role) {
          setRole(data.role.charAt(0).toUpperCase() + data.role.slice(1));
        }
      })
      .catch(err => console.error("Error reading session for chatbot:", err));

    return () => {
      isMounted = false;
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, loading, isOpen]);

  // Only render for Student or Admin
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
    <div className="fixed bottom-6 right-6 z-[9999] font-sans">
      {/* Floating Chat Bubble Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 bg-blue-600 hover:bg-blue-700 text-white hover:scale-110 relative active:scale-95 border-2 border-white"
        >
          <MessageSquare className="w-6 h-6 animate-pulse" />
          <div className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-rose-500 rounded-full border-2 border-white animate-ping"></div>
          <div className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-rose-500 rounded-full border-2 border-white"></div>
        </button>
      )}

      {/* Floating Chat Panel */}
      {isOpen && (
        <div className="w-80 sm:w-96 h-[480px] rounded-2xl border border-slate-200 bg-white/95 backdrop-blur-md shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-5 duration-300">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-700 to-indigo-600 p-4 text-white flex items-center justify-between shadow-md">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center border border-white/10">
                <Bot className="w-4.5 h-4.5 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold leading-none">Placement Chatbot</h3>
                <span className="text-[10px] text-white/70 leading-none">RADIX Assistant</span>
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-lg hover:bg-white/10 text-white/80 hover:text-white transition-colors"
                title="Minimize"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-lg hover:bg-white/10 text-white/80 hover:text-white transition-colors"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin bg-slate-55/30">
            {messages.map((msg, index) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={index}
                  className={`flex gap-2 max-w-[85%] ${isUser ? "ml-auto flex-row-reverse" : ""}`}
                >
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-semibold border ${
                      isUser 
                        ? "bg-blue-600 text-white border-blue-600" 
                        : "bg-slate-100 text-slate-600 border-slate-200"
                    }`}
                  >
                    {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                  </div>

                  <div className="flex flex-col gap-1">
                    <div
                      className={`px-3 py-2 rounded-xl text-xs leading-relaxed whitespace-pre-wrap shadow-sm ${
                        isUser 
                          ? "bg-blue-600 text-white rounded-tr-none" 
                          : "bg-slate-50 text-slate-800 rounded-tl-none border border-slate-100"
                      }`}
                    >
                      {msg.content}
                    </div>

                    {!isUser && msg.context && msg.context.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-0.5 px-0.5">
                        {msg.context.map((source, sIdx) => (
                          <span 
                            key={sIdx} 
                            className="bg-slate-100 border border-slate-200 text-[8px] font-bold text-slate-600 px-1 py-0.5 rounded"
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

            {loading && (
              <div className="flex gap-2 max-w-[80%]">
                <div className="w-7 h-7 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-3.5 h-3.5 animate-bounce" />
                </div>
                <div className="bg-slate-50 border border-slate-100 rounded-xl rounded-tl-none px-3 py-2 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="p-3 border-t border-slate-200 bg-slate-50 flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot..."
              className="flex-1 bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 text-slate-800 px-3 py-2 rounded-xl text-xs focus:outline-none transition-all duration-300 placeholder:text-slate-400"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white w-8 h-8 rounded-xl flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
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
