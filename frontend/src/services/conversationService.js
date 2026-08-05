import * as conversationApi from "../api/conversationApi";

export async function getConversations() {
    return await conversationApi.getConversations();
}

export async function createConversation() {
    return await conversationApi.createConversation();
}

export async function deleteConversation(sessionId) {

    return await conversationApi.deleteConversation(
        sessionId
    );

}