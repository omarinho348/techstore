import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

import { useAuth } from "./AuthContext";
import * as conversationService from "../services/conversationService";

const ConversationContext = createContext();

export function ConversationProvider({ children }) {

    const { user } = useAuth();

    const [conversations, setConversations] = useState([]);

    const [currentSessionId, setCurrentSessionId] =
        useState(null);

    async function loadConversations() {

        const data =
            await conversationService.getConversations();

        setConversations(data);

        setCurrentSessionId((previousSessionId) => {

            if (
                previousSessionId &&
                data.some((conversation) =>
                    conversation.session_id === previousSessionId
                )
            ) {
                return previousSessionId;
            }

            return data[0]?.session_id ?? null;

        });

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

        if (!user) {

            setConversations([]);
            setCurrentSessionId(null);

            return;

        }

        loadConversations();

    }, [user]);

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