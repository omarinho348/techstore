import * as authApi from "../api/authApi";
import { getUser, saveUser, removeUser } from "../utils/storage";

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

export async function getMe() {
    return authApi.getMe();
}

export async function updateProfile(data) {
    const result = await authApi.updateMe(data);
    const currentUser = getUser();

    const updatedUser = {
        ...currentUser,
        ...result,
    };

    saveUser(updatedUser);

    return updatedUser;
}