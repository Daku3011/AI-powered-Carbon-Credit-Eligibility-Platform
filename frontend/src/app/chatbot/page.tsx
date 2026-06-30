"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Send, User, Bot, FileText, Sparkles, MessageCircle } from "lucide-react";
import { queryChatbot, type ChatbotResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

const suggestedQueries = [
  "How to register a solar project under Indian Carbon Market?",
  "What are the eligibility criteria for carbon credit verification?",
  "Explain the difference between CDM and ICM methodologies.",
  "What documents are needed for carbon credit registration?",
  "How does solid waste management earn carbon offsets?",
];

function parseInlineMarkdown(text: string, isUser: boolean): React.ReactNode[] {
  const regex = /(\*\*.*?\*\*|`.*?`|\*.*?\*)/g;
  const parts = text.split(regex);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className={`font-semibold ${isUser ? "text-white font-bold" : "text-neutral-900 dark:text-white"}`}>
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={index} className={`px-1.5 py-0.5 rounded text-xs font-mono font-bold border ${isUser ? "bg-emerald-700/30 border-emerald-600/30 text-white" : "bg-neutral-100 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700"}`}>
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return (
        <em key={index} className="italic">
          {part.slice(1, -1)}
        </em>
      );
    }
    return part;
  });
}

function MarkdownRenderer({ content, isUser }: { content: string; isUser: boolean }) {
  const blockRegex = /(```[\s\S]*?```)/g;
  const blocks = content.split(blockRegex);

  return (
    <div className={`space-y-2 text-sm leading-relaxed ${isUser ? "text-emerald-50" : "text-neutral-750 dark:text-neutral-300"}`}>
      {blocks.map((block, index) => {
        if (block.startsWith("```") && block.endsWith("```")) {
          const lines = block.split("\n");
          const firstLine = lines[0].slice(3).trim();
          const codeContent = lines.slice(1, -1).join("\n");
          return (
            <div key={index} className="relative my-2 rounded bg-neutral-950 p-3 text-neutral-50 border border-neutral-800 overflow-x-auto font-mono text-xs">
              {firstLine && (
                <div className="absolute right-2 top-2 text-[10px] text-neutral-500 uppercase font-sans tracking-wider">
                  {firstLine}
                </div>
              )}
              <pre>
                <code>{codeContent}</code>
              </pre>
            </div>
          );
        }

        const lines = block.split("\n");
        const renderedElements: React.ReactNode[] = [];
        let currentList: { type: "ul" | "ol"; items: string[] } | null = null;

        const flushList = (key: number) => {
          if (currentList) {
            const ListTag = currentList.type;
            renderedElements.push(
              <ListTag
                key={`list-${key}`}
                className={
                  currentList.type === "ul"
                    ? "list-disc pl-5 my-2 space-y-1"
                    : "list-decimal pl-5 my-2 space-y-1"
                }
              >
                {currentList.items.map((item, itemIdx) => (
                  <li key={itemIdx}>{parseInlineMarkdown(item, isUser)}</li>
                ))}
              </ListTag>
            );
            currentList = null;
          }
        };

        lines.forEach((line, lineIdx) => {
          const trimmed = line.trim();
          if (!trimmed) {
            flushList(lineIdx);
            return;
          }

          if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
            if (!currentList || currentList.type !== "ul") {
              flushList(lineIdx);
              currentList = { type: "ul", items: [] };
            }
            currentList.items.push(trimmed.slice(2));
            return;
          }

          const matchNumbered = trimmed.match(/^(\d+)\.\s(.*)/);
          if (matchNumbered) {
            if (!currentList || currentList.type !== "ol") {
              flushList(lineIdx);
              currentList = { type: "ol", items: [] };
            }
            currentList.items.push(matchNumbered[2]);
            return;
          }

          flushList(lineIdx);

          if (trimmed.startsWith("### ")) {
            renderedElements.push(
              <h3 key={lineIdx} className="text-sm font-bold mt-3 mb-1">
                {parseInlineMarkdown(trimmed.slice(4), isUser)}
              </h3>
            );
          } else if (trimmed.startsWith("## ")) {
            renderedElements.push(
              <h2 key={lineIdx} className="text-base font-bold mt-4 mb-2">
                {parseInlineMarkdown(trimmed.slice(3), isUser)}
              </h2>
            );
          } else if (trimmed.startsWith("# ")) {
            renderedElements.push(
              <h1 key={lineIdx} className="text-lg font-bold mt-4 mb-2">
                {parseInlineMarkdown(trimmed.slice(2), isUser)}
              </h1>
            );
          } else {
            renderedElements.push(
              <p key={lineIdx} className="my-1">
                {parseInlineMarkdown(trimmed, isUser)}
              </p>
            );
          }
        });

        flushList(lines.length);

        return <div key={index}>{renderedElements}</div>;
      })}
    </div>
  );
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (query: string) => {
    if (!query.trim() || loading) return;

    const userMessage: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response: ChatbotResponse = await queryChatbot({ query });
      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-8 max-w-5xl mx-auto flex flex-col h-[calc(100vh-120px)]">
      {/* Page Title */}
      <div className="mb-6 flex-shrink-0">
        <h1 className="text-3xl font-extrabold tracking-tight text-neutral-900 dark:text-neutral-100">
          AI Carbon Consultant
        </h1>
        <p className="text-neutral-500 dark:text-neutral-400 text-sm">
          Gemini-powered advisory panel for policy guidelines, compliance standards, and registration pathways.
        </p>
      </div>

      {/* Grid Layout (2 Cols: Chat Panel & Sidebar) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 overflow-hidden min-h-[400px]">
        {/* Chat Panel */}
        <Card className="lg:col-span-3 flex flex-col overflow-hidden border border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md shadow-lg">
          <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-neutral-450 dark:text-neutral-400 py-16">
                <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                  <Bot className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
                </div>
                <h3 className="font-bold text-neutral-700 dark:text-neutral-300 text-base mb-1">
                  Indian Carbon Market Advisory
                </h3>
                <p className="text-sm max-w-xs mx-auto mb-4">
                  Ask details on BEE compliance, registration certificates, or credits validation.
                </p>
                <div className="lg:hidden grid gap-2 max-w-sm mx-auto">
                  {suggestedQueries.map((query, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      onClick={() => handleSend(query)}
                      className="text-left justify-start text-xs border-neutral-200 dark:border-neutral-800 hover:bg-neutral-100 dark:hover:bg-neutral-800 cursor-pointer"
                    >
                      {query}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((message, i) => (
              <div
                key={i}
                className={`flex gap-3 items-start ${
                  message.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full shadow-sm ${
                    message.role === "user"
                      ? "bg-emerald-600 text-white"
                      : "bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  )}
                </div>
                <div
                  className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                    message.role === "user"
                      ? "bg-emerald-600 text-white rounded-tr-none"
                      : "bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-tl-none"
                  }`}
                >
                  {/* Avatar Label */}
                  <span className={`text-[10px] uppercase font-bold block mb-1 opacity-70 ${message.role === "user" ? "text-emerald-100" : "text-neutral-400"}`}>
                    {message.role === "user" ? "User" : "AI Consultant"}
                  </span>
                  <MarkdownRenderer content={message.content} isUser={message.role === "user"} />
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className={`mt-3 pt-2 border-t ${message.role === "user" ? "border-emerald-500/20" : "border-neutral-200 dark:border-neutral-800"}`}>
                      <p className="text-[10px] font-semibold opacity-70 mb-1">Sources & Policies:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {message.sources.map((source, j) => (
                          <span
                            key={j}
                            className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full border ${
                              message.role === "user"
                                ? "bg-emerald-500/20 border-emerald-500/30 text-emerald-100"
                                : "bg-white dark:bg-neutral-950 border-neutral-200 dark:border-neutral-800 text-neutral-500"
                            }`}
                          >
                            <FileText className="h-2.5 w-2.5" />
                            {source}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 items-start">
                <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm animate-pulse">
                  <Bot className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div className="bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl rounded-tl-none p-4 shadow-sm">
                  <p className="text-xs text-neutral-450 dark:text-neutral-400 animate-pulse flex items-center gap-1.5">
                    Analyzing policies...
                  </p>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex-shrink-0 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-900/30 p-4">
            <div className="flex w-full gap-2">
              <Input
                placeholder="Ask a question about carbon registries or MSME transition..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend(input);
                  }
                }}
                disabled={loading}
                className="bg-white dark:bg-neutral-950 border-neutral-300 dark:border-neutral-700 focus-visible:ring-emerald-500 focus-visible:border-emerald-500"
              />
              <Button onClick={() => handleSend(input)} disabled={loading || !input.trim()} className="bg-emerald-600 hover:bg-emerald-700 text-white shadow cursor-pointer">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardFooter>
        </Card>

        {/* Sidebar - Desktop only Suggested Queries */}
        <Card className="hidden lg:flex flex-col border border-neutral-200 dark:border-neutral-800 bg-white/70 dark:bg-neutral-900/50 backdrop-blur-md p-4 shadow-lg h-full overflow-y-auto">
          <CardHeader className="p-0 pb-4 border-b border-neutral-200 dark:border-neutral-800">
            <CardTitle className="text-sm font-bold flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-emerald-500" />
              Quick Consults
            </CardTitle>
            <CardDescription className="text-xs">
              Click a suggested query to consult Gemini instantly.
            </CardDescription>
          </CardHeader>
          <div className="pt-4 space-y-2">
            {suggestedQueries.map((query, i) => (
              <Button
                key={i}
                variant="outline"
                size="sm"
                onClick={() => handleSend(query)}
                className="w-full text-left justify-start h-auto py-2.5 px-3 whitespace-normal text-xs border-neutral-200 dark:border-neutral-800 hover:bg-emerald-500/5 hover:border-emerald-500/20 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors flex items-start gap-2 cursor-pointer group"
              >
                <MessageCircle className="h-3.5 w-3.5 mt-0.5 text-neutral-400 group-hover:text-emerald-500 flex-shrink-0" />
                <span>{query}</span>
              </Button>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
