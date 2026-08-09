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

export async function uploadImage(sessionId, file) {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user?.access_token) {
        throw new Error("No access token found.");
    }

    const form = new FormData();
    form.append("session_id", sessionId);
    form.append("file", file, file.name);

    const response = await fetch("http://127.0.0.1:8000/chat/upload", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${user.access_token}`,
        },
        body: form,
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Upload failed");
    }

    return await response.json();
}