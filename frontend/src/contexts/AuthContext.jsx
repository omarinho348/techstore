import { createContext, useContext, useEffect, useState } from "react";

import * as authService from "../services/authService";
import { getUser } from "../utils/storage";

const AuthContext = createContext();

export function AuthProvider({ children }) {

    const [user, setUser] = useState(null);

    const [loading, setLoading] = useState(true);

    useEffect(() => {

        async function initializeAuth() {

            const savedUser = getUser();

            if (!savedUser) {

                setLoading(false);

                return;

            }

            try {

                const profile = await authService.getMe();

                setUser({
                    ...savedUser,
                    ...profile,
                });

            } catch {

                setUser(savedUser);

            }

            setLoading(false);

        }

        initializeAuth();

    }, []);

    async function login(credentials) {

        const result = await authService.login(credentials);

        setUser(result);

        return result;
    }

    async function register(data) {

        const result = await authService.register(data);

        setUser(result);

        return result;
    }

    function logout() {

        authService.logout();

        setUser(null);

    }

    async function updateProfile(data) {

        const result = await authService.updateProfile(data);

        setUser(result);

        return result;

    }

    return (

        <AuthContext.Provider

            value={{
                user,
                loading,
                login,
                register,
                updateProfile,
                logout,
            }}

        >

            {children}

        </AuthContext.Provider>

    );

}

export function useAuth() {

    return useContext(AuthContext);

}