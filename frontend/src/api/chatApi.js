import api from "./axios";

function dispatchEvent(rawEvent, handlers) {
    const lines = rawEvent.split("\n");
    const eventType = lines.find((line) => line.startsWith("event:"))?.slice(6).trim();
    const payload = lines.find((line) => line.startsWith("data:"))?.slice(5).trim();

    if (!eventType || !payload) return;

    const data = JSON.parse(payload);
    if (eventType === "error") {
        throw new Error(data.message || "The response stream failed.");
    }

    handlers?.[eventType]?.(data);
}

export async function sendMessage(data, handlers) {
    const user = JSON.parse(localStorage.getItem("user"));
    const token = user?.access_token;

    if (!token) throw new Error("No access token found.");

    const response = await fetch("http://127.0.0.1:8000/chat/stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
    });

    if (!response.ok || !response.body) {
        throw new Error((await response.text()) || "Unable to start the response stream.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });

        const events = buffer.split("\n\n");
        buffer = events.pop();
        events.filter(Boolean).forEach((event) => dispatchEvent(event, handlers));

        if (done) {
            if (buffer.trim()) dispatchEvent(buffer, handlers);
            break;
        }
    }
}

export async function getConversation(sessionId) {
    const response = await api.get(`/chat/${sessionId}`);
    return response.data;
}

export async function deleteConversation(sessionId) {
    const response = await api.delete(`/chat/${sessionId}`);
    return response.data;
}
