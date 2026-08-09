export function saveUser(user) {
    localStorage.setItem(
        "user",
        JSON.stringify(user)
    );
}

export function getUser() {
    const user = localStorage.getItem("user");

    return user
        ? JSON.parse(user)
        : null;
}

export function removeUser() {
    localStorage.removeItem("user");
}

export function getSessionId() {

    let sessionId =
        localStorage.getItem("session_id");

    if (!sessionId) {

        sessionId = crypto.randomUUID();

        localStorage.setItem(
            "session_id",
            sessionId,
        );

    }

    return sessionId;

}

export function newSession() {

    const sessionId =
        crypto.randomUUID();

    localStorage.setItem(
        "session_id",
        sessionId,
    );

    return sessionId;

}