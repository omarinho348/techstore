import { useEffect, useState } from "react";
import { useRef } from "react";

import MainLayout from "../layouts/MainLayout";

import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

import * as chatService from "../services/chatService";

import { useAuth } from "../contexts/AuthContext";
import { useConversations } from "../contexts/ConversationContext";

export default function Chat() {

    const [messages, setMessages] = useState([]);
    const skipNextEmptyHistoryLoad = useRef(false);
    const typingQueue = useRef("");
    const typingTimer = useRef(null);

    const { user } = useAuth();

    const {
        currentSessionId,
        loadConversations,
        newConversation,
    } = useConversations();

    useEffect(() => {

        async function loadHistory() {

            if (!currentSessionId) {

                setMessages([]);

                return;

            }

            try {

                const result =
                    await chatService.loadConversation(
                        currentSessionId
                    );

                if (
                    skipNextEmptyHistoryLoad.current &&
                    (result.messages ?? []).length === 0
                ) {
                    skipNextEmptyHistoryLoad.current = false;
                    return;
                }

                skipNextEmptyHistoryLoad.current = false;

                setMessages(result.messages ?? []);

            }

            catch {

                setMessages([]);

            }

        }

        loadHistory();

        return () => {
            stopTypingTimer();
            typingQueue.current = "";
        };

    }, [currentSessionId]);

    function stopTypingTimer() {
        if (typingTimer.current) {
            clearInterval(typingTimer.current);
            typingTimer.current = null;
        }
    }

    function startTypingTimer() {
        if (typingTimer.current) {
            return;
        }

        typingTimer.current = setInterval(() => {
            if (!typingQueue.current) {
                stopTypingTimer();
                return;
            }

            const nextChar = typingQueue.current[0];
            typingQueue.current = typingQueue.current.slice(1);

            setMessages((previous) => {
                const updated = [...previous];

                if (updated.length === 0) {
                    return previous;
                }

                const lastIndex = updated.length - 1;
                updated[lastIndex] = {
                    ...updated[lastIndex],
                    message:
                        (updated[lastIndex].message ?? "") + nextChar,
                };

                return updated;
            });

        }, 16);
    }

    async function handleSend(message) {

    stopTypingTimer();
    typingQueue.current = "";

    let sessionId = currentSessionId;

    if (!sessionId) {
        skipNextEmptyHistoryLoad.current = true;
        sessionId = await newConversation();
    }

    if (!sessionId) {
        return;
    }

    // ==========================================================
    // Add user message
    // ==========================================================

    setMessages((previous) => [

        ...previous,

        {
            role: "user",
            message,
        },

        {
            role: "assistant",
            message: "",
            status: "Thinking...",
            agent: "",
        },

    ]);

    await loadConversations();

    await chatService.sendMessage(

        sessionId,

        message,

        {

            // --------------------------------------------------

            agent: ({ name }) => {

                setMessages((previous) => {

                    const updated = [...previous];

                    updated[updated.length - 1] = {

                        ...updated[updated.length - 1],

                        agent: name,

                    };

                    return updated;

                });

            },

            // --------------------------------------------------

            status: ({ text }) => {

                setMessages((previous) => {

                    const updated = [...previous];

                    updated[updated.length - 1] = {

                        ...updated[updated.length - 1],

                        status: text,

                    };

                    return updated;

                });

            },

            // --------------------------------------------------

            token: ({ text }) => {
                typingQueue.current += text;
                startTypingTimer();

            },

            // --------------------------------------------------

            done: () => {

                if (!typingQueue.current) {
                    stopTypingTimer();
                }

                setMessages((previous) => {

                    const updated = [...previous];

                    updated[updated.length - 1] = {

                        ...updated[updated.length - 1],

                        status: "",

                    };

                    return updated;

                });

            },

        },

    );

}

    return (

        <MainLayout>

            <div className="flex h-full flex-col">

                <ChatWindow
                    messages={messages}
                    userName={user?.name}
                />

                <ChatInput
                    onSend={handleSend}
                />

            </div>

        </MainLayout>

    );

}