import api from "./axios";

export async function register(data) {
    const response = await api.post("/auth/register", data);
    return response.data;
}

export async function login(data) {
    const response = await api.post("/auth/login", data);
    return response.data;
}

export async function getMe() {
    const response = await api.get("/me");
    return response.data;
}

export async function updateMe(data) {
    const response = await api.patch("/me", data);
    return response.data;
}