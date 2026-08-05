import api from "./axios";

export async function getConversations() {

    const response = await api.get("/conversations");

    return response.data;

}

export async function createConversation() {

    const response = await api.post("/conversations");

    return response.data;

}

export async function deleteConversation(sessionId) {

    const response = await api.delete(
        `/conversations/${sessionId}`
    );

    return response.data;

}