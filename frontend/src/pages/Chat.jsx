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
        if (!sessionId) return;

        setMessages((previous) => [
            ...previous,
            { role: "user", message },
            { role: "assistant", message: "", status: "Thinking...", agent: "" },
        ]);
        await loadConversations();

        try {
            await chatService.sendMessage(sessionId, message, {
                agent: ({ name }) => {
                    setMessages((previous) => replaceLastMessage(previous, { agent: name }));
                },
                status: ({ text }) => {
                    setMessages((previous) => replaceLastMessage(previous, { status: text }));
                },
                token: ({ text }) => {
                    typingQueue.current += text;
                    startTypingTimer();
                },
                final: ({ response }) => {
                    stopTypingTimer();
                    typingQueue.current = "";
                    setMessages((previous) => replaceLastMessage(previous, {
                        message: response,
                        status: "",
                    }));
                },
                done: () => {
                    setMessages((previous) => replaceLastMessage(previous, { status: "" }));
                },
            });
        } catch (error) {
            stopTypingTimer();
            typingQueue.current = "";
            setMessages((previous) => replaceLastMessage(previous, {
                message: error.message || "[Message processing failed]",
                status: "",
            }));
        }
    }

    function replaceLastMessage(messages, changes) {
        const updated = [...messages];
        const lastIndex = updated.length - 1;
        updated[lastIndex] = { ...updated[lastIndex], ...changes };
        return updated;
    }

// attach uploadImage method to handleSend so child can call it
handleSend.uploadImage = async function (file) {
    stopTypingTimer();
    typingQueue.current = "";

    let sessionId = currentSessionId;

    if (!sessionId) {
        skipNextEmptyHistoryLoad.current = true;
        sessionId = await newConversation();
    }

    if (!sessionId) return;

    setMessages((previous) => [
        ...previous,
        {
            role: "user",
            message: `[Image uploaded: ${file.name}]`,
        },
        {
            role: "assistant",
            message: "",
            status: "Processing image...",
            agent: "",
        },
    ]);

    await loadConversations();

    try {
        const result = await chatService.uploadImage(sessionId, file);

        // show assistant response
        const assistantText = result.response ?? "[No response]";

        setMessages((previous) => {
            const updated = [...previous];

            updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                message: assistantText,
                status: "",
            };

            return updated;
        });

    } catch (err) {
        setMessages((previous) => {
            const updated = [...previous];

            updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                message: "[Image processing failed]",
                status: "",
            };

            return updated;
        });
    }
};

    return (

        <MainLayout>

            <div className="flex h-full flex-col">

                <ChatWindow
                    messages={messages}
                    userName={user?.name}
                />

                <ChatInput
                    onSend={handleSend}
                    // expose uploadImage helper via onSend.uploadImage
                    ref={null}
                />


            </div>

        </MainLayout>

    );

}
