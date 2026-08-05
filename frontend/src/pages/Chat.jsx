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

        setMessages((previous) => [

            ...previous,

            {
                role: "user",
                message,
            },

        ]);

        const response =
            await chatService.sendMessage(
                currentSessionId,
                message,
            );

        await loadConversations();    

        setMessages((previous) => [

            ...previous,

            {
                role: "assistant",
                message: response.response,
            },

        ]);

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