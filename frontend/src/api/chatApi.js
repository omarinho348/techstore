import api from "./axios";

export async function sendMessage(data, handlers) {

    const user = JSON.parse(
    localStorage.getItem("user")
);

const token =
    user?.access_token;

    if (!token) {

    throw new Error(
        "No access token found."
    );

}

    const response =
        await fetch(
            "http://127.0.0.1:8000/chat/stream",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "Authorization":
                        `Bearer ${token}`,

                },

                body: JSON.stringify(data),

            },
        );

    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    let buffer = "";

    while (true) {

        const {
            value,
            done,
        } = await reader.read();

        if (done)
            break;

        buffer += decoder.decode(
            value,
            {
                stream: true,
            },
        );

        const events =
            buffer.split("\n\n");

        buffer =
            events.pop();

        for (const event of events) {

            const lines =
                event.split("\n");

            let eventType = "";

            let payload = "";

            for (const line of lines) {

                if (
                    line.startsWith("event:")
                ) {

                    eventType =
                        line.replace(
                            "event:",
                            "",
                        ).trim();

                }

                if (
                    line.startsWith("data:")
                ) {

                    payload =
                        line.replace(
                            "data:",
                            "",
                        ).trim();

                }

            }

            if (!payload)
                continue;

            const json =
                JSON.parse(payload);

            handlers?.[eventType]?.(
                json,
            );

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