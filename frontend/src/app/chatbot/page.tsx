"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Send, User, Bot, FileText } from "lucide-react";
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
];

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
    } catch (error) {
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
    <div className="container py-8 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">AI Carbon Consultant</h1>
        <p className="text-muted-foreground mt-1">
          Ask about Indian carbon markets, policies, and registration processes.
        </p>
      </div>

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="space-y-4 min-h-[300px] max-h-[500px] overflow-y-auto">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-12">
                <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="mb-4">Ask me anything about carbon credits</p>
                <div className="grid gap-2 max-w-md mx-auto">
                  {suggestedQueries.map((query, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      onClick={() => handleSend(query)}
                      className="text-left justify-start"
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
                className={`flex gap-3 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs opacity-70 mb-1">Sources:</p>
                      <div className="flex flex-wrap gap-1">
                        {message.sources.map((source, j) => (
                          <span
                            key={j}
                            className="inline-flex items-center gap-1 text-xs opacity-70"
                          >
                            <FileText className="h-3 w-3" />
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
              <div className="flex gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-muted rounded-lg p-3">
                  <p className="text-sm animate-pulse">Thinking...</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Input
          placeholder="Ask about carbon markets, policies, or registration..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend(input);
            }
          }}
          disabled={loading}
        />
        <Button onClick={() => handleSend(input)} disabled={loading || !input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
