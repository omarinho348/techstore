import api from "./axios";

export async function sendVoice(audioBlob, sessionId) {

    const formData = new FormData();

    formData.append(
        "audio",
        audioBlob,
        "recording.webm",
    );

    formData.append(
        "session_id",
        sessionId,
    );

    const response = await api.post(
        "/voice",
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data",
            },
        },
    );

    return response.data;
}