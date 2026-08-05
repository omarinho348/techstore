import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import * as conversationService from "../services/conversationService";

const ConversationContext = createContext();

export function ConversationProvider({ children }) {

    const [conversations, setConversations] = useState([]);

    const [currentSessionId, setCurrentSessionId] =
        useState(null);

    async function loadConversations() {

        const data =
            await conversationService.getConversations();

        setConversations(data);

        // Only choose a default conversation
        // if none is currently selected.
        if (!currentSessionId && data.length > 0) {

            setCurrentSessionId(
                data[0].session_id
            );

        }

    }

    async function newConversation() {

        const conversation =
            await conversationService.createConversation();

        await loadConversations();

        setCurrentSessionId(
            conversation.session_id
        );

        return conversation.session_id;

    }

    async function deleteConversation(sessionId) {

    await conversationService.deleteConversation(
        sessionId
    );

    await loadConversations();

    if (currentSessionId === sessionId) {

        const remaining =
            await conversationService.getConversations();

        if (remaining.length > 0) {

            setCurrentSessionId(
                remaining[0].session_id
            );

        }

        else {

            setCurrentSessionId(null);

        }

    }

}

    useEffect(() => {

        loadConversations();

    }, []);

    return (

        <ConversationContext.Provider

            value={{

                conversations,

                currentSessionId,

                setCurrentSessionId,

                loadConversations,

                newConversation,

                deleteConversation,

            }}

        >

            {children}

        </ConversationContext.Provider>

    );

}

export function useConversations() {

    return useContext(ConversationContext);

}