import api from "./axios";

export async function sendMessage(data) {
    const response = await api.post("/chat", data);

    return response.data;
}

export async function getConversation(sessionId) {
    const response = await api.get(`/chat/${sessionId}`);

    return response.data;
}

export async function deleteConversation(sessionId) {
    const response = await api.delete(`/chat/${sessionId}`);

    return response.data;
}