import { useEffect, useState } from "react";

import MainLayout from "../layouts/MainLayout";

import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";

import * as chatService from "../services/chatService";

import { useConversations } from "../contexts/ConversationContext";

export default function Chat() {

    const [messages, setMessages] = useState([]);

    const {
        currentSessionId,
        loadConversations,
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

                setMessages(result.messages ?? []);

            }

            catch {

                setMessages([]);

            }

        }

        loadHistory();

    }, [currentSessionId]);

    async function handleSend(message) {

    if (!currentSessionId)
        return;

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

        currentSessionId,

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

                setMessages((previous) => {

                    const updated = [...previous];

                    updated[updated.length - 1] = {

                        ...updated[updated.length - 1],

                        message:

                            updated[
                                updated.length - 1
                            ].message + text,

                    };

                    return updated;

                });

            },

            // --------------------------------------------------

            done: () => {

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
                />

                <ChatInput
                    onSend={handleSend}
                />

            </div>

        </MainLayout>

    );

}