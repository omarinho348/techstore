import * as chatApi from "../api/chatApi";

export async function sendMessage(
    sessionId,
    message,
    handlers,
) {

    return await chatApi.sendMessage(

        {

            session_id: sessionId,

            message,

        },

        handlers,

    );

}

export async function loadConversation(
    sessionId,
) {

    return await chatApi.getConversation(
        sessionId,
    );

}

export async function deleteConversation(
    sessionId,
) {

    return await chatApi.deleteConversation(
        sessionId,
    );

}