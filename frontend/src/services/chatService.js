import * as chatApi from "../api/chatApi";

export async function sendMessage(sessionId, message) {
    return await chatApi.sendMessage({
        session_id: sessionId,
        message,
    });
}

export async function loadConversation(sessionId) {
    return await chatApi.getConversation(sessionId);
}

export async function deleteConversation(sessionId) {
    return await chatApi.deleteConversation(sessionId);
}