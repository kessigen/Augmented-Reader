"use client";

import React, { useState, useRef, useEffect } from "react";
import Image from "next/image";
import "./PopChat.css";

interface Message {
  sender: "user" | "bot";
  text: string;
}

interface PopChatProps {
  bookId: number;
  apiBaseUrl?: string;
}

const PopChat: React.FC<PopChatProps> = ({
  bookId,
  apiBaseUrl = "http://127.0.0.1:8000/api",
}) => {
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const msgAreaRef = useRef<HTMLDivElement>(null);

  const toggleChat = () => setChatOpen((p) => !p);

  
  useEffect(() => {
    msgAreaRef.current?.scrollTo({
      top: msgAreaRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  useEffect(() => {
    document.body.classList.toggle("chat-open", chatOpen);
    return () => document.body.classList.remove("chat-open");
  }, [chatOpen]);

  const handleSend = async () => {
    const text = inputRef.current?.value?.trim();
    if (!text) return;
    inputRef.current!.value = "";

    setMessages((prev) => [...prev, { sender: "user", text }]);
    setLoading(true);

    try {
      const res = await fetch(
        `${apiBaseUrl}/books/query/${bookId}/${encodeURIComponent(text)}/`
      );
      const data = await res.json();
      const answer = data.summary || data.answer || "No response.";

      
      setMessages((prev) => [...prev, { sender: "bot", text: answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: " Could not reach the server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div id="chatCon">
      <div
        className="chat-box text-black"
        style={{ display: chatOpen ? "flex" : "none" }}
      >
        <div className="header">
          <span>Ask the Book Assistant</span>
          <button className="close-btn" onClick={toggleChat} aria-label="Close">
            X
          </button>
        </div>

        <div className="msg-area" ref={msgAreaRef}>
          {messages.map((msg, i) => (
            <p key={i} className={msg.sender === "user" ? "right" : "left"}>
              <span>{msg.text}</span>
            </p>
          ))}
          {loading && (
            <p className="left">
              <span>Book Assistant is thinking…</span>
            </p>
          )}
        </div>

        <div className="footer px-2">
          <input
            type="text"
            ref={inputRef}
            placeholder="Ask a question..."
            onKeyDown={handleKeyDown}
          />
          <button onClick={handleSend}>
            <i className="fa fa-paper-plane" />
          </button>
        </div>
      </div>

      {!chatOpen && (
       <div className="pop">
  <img
    onClick={toggleChat}
    src="https://p7.hiclipart.com/preview/151/758/442/iphone-imessage-messages-logo-computer-icons-message.jpg"
    alt="Chat icon"
    width={60}
    height={60}
    style={{ borderRadius: "50%", cursor: "pointer" }}
  />
</div>
      )}
    </div>
  );
};

export default PopChat;
