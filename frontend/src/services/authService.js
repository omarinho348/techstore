import * as authApi from "../api/authApi";
import { saveUser, removeUser } from "../utils/storage";

export async function register(data) {
    const result = await authApi.register(data);

    saveUser(result);

    return result;
}

export async function login(data) {
    const result = await authApi.login(data);

    saveUser(result);

    return result;
}

export function logout() {
    removeUser();
}