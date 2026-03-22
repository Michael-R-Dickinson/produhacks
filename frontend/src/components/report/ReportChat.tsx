import { useState, useRef, useEffect, useCallback } from "react";
import Markdown, { defaultUrlTransform } from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send } from "lucide-react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
}

interface Props {
    reportMarkdown: string;
}

const SUGGESTIONS = [
    "Summarize the key risks",
    "What sectors should I rebalance?",
    "Explain the contradictions",
];

function allowDataUrls(url: string): string {
    if (url.startsWith("data:")) return url;
    return defaultUrlTransform(url);
}

export default function ReportChat({ reportMarkdown }: Props) {
    const apiUrl = import.meta.env.VITE_API_URL as string | undefined;

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [streaming, setStreaming] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const sentinelRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        sentinelRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, streaming]);

    const sendMessage = useCallback(async (text: string) => {
        const trimmed = text.trim();
        if (!trimmed || isLoading || !apiUrl) return;

        const userMessage: Message = {
            id: crypto.randomUUID(),
            role: "user",
            content: trimmed,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);
        setStreaming("");

        const history = messages.map((m) => ({
            role: m.role === "assistant" ? "model" : "user",
            parts: [{ text: m.content }],
        }));

        try {
            const response = await fetch(`${apiUrl}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: trimmed,
                    history,
                    report_context: reportMarkdown,
                }),
            });

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulated = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split("\n");

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;
                    const raw = line.slice(6).trim();
                    if (!raw) continue;

                    try {
                        const parsed: { token: string; done: boolean } = JSON.parse(raw);
                        if (parsed.done) {
                            const finalContent = accumulated;
                            setMessages((prev) => [
                                ...prev,
                                {
                                    id: crypto.randomUUID(),
                                    role: "assistant",
                                    content: finalContent,
                                },
                            ]);
                            setStreaming("");
                            accumulated = "";
                        } else {
                            accumulated += parsed.token;
                            setStreaming(accumulated);
                        }
                    } catch {
                        // ignore malformed SSE lines
                    }
                }
            }
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                {
                    id: crypto.randomUUID(),
                    role: "assistant",
                    content: "Sorry, something went wrong. Please try again.",
                },
            ]);
            setStreaming("");
        } finally {
            setIsLoading(false);
        }
    }, [messages, isLoading, apiUrl, reportMarkdown]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input);
        }
    };

    return (
        <div className="report-chat">
            <div className="report-chat-header">Ask about this report</div>
            <div className="report-chat-subtitle">
                Get answers grounded in your portfolio data and today's analysis.
            </div>

            {messages.length > 0 || streaming ? (
                <div className="report-chat-thread">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`report-chat-message ${msg.role}`}
                        >
                            <div className="report-chat-message-avatar">
                                {msg.role === "assistant" ? "AI" : "Me"}
                            </div>
                            <div className="report-chat-message-bubble">
                                {msg.role === "assistant" ? (
                                    <Markdown
                                        remarkPlugins={[remarkGfm]}
                                        urlTransform={allowDataUrls}
                                    >
                                        {msg.content}
                                    </Markdown>
                                ) : (
                                    msg.content
                                )}
                            </div>
                        </div>
                    ))}

                    {streaming && (
                        <div className="report-chat-message assistant">
                            <div className="report-chat-message-avatar">AI</div>
                            <div className="report-chat-message-bubble">
                                <Markdown
                                    remarkPlugins={[remarkGfm]}
                                    urlTransform={allowDataUrls}
                                >
                                    {streaming}
                                </Markdown>
                            </div>
                        </div>
                    )}

                    <div ref={sentinelRef} />
                </div>
            ) : null}

            {apiUrl ? (
                <div className="report-chat-input-area">
                    {messages.length === 0 && !streaming && (
                        <div className="report-chat-suggestions">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    className="report-chat-suggestion-chip"
                                    onClick={() => sendMessage(s)}
                                    disabled={isLoading}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}
                    <div className="report-chat-input-bar">
                        <input
                            type="text"
                            placeholder="Ask a question about your report..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={isLoading}
                        />
                        <button
                            className="report-chat-send-btn"
                            onClick={() => sendMessage(input)}
                            disabled={isLoading || !input.trim()}
                        >
                            <Send size={14} />
                        </button>
                    </div>
                </div>
            ) : (
                <div className="report-chat-unavailable">
                    Chat unavailable -- backend not connected
                </div>
            )}
        </div>
    );
}
