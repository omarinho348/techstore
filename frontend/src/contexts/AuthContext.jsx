import { createContext, useContext, useEffect, useState } from "react";

import * as authService from "../services/authService";
import { getUser } from "../utils/storage";

const AuthContext = createContext();

export function AuthProvider({ children }) {

    const [user, setUser] = useState(null);

    const [loading, setLoading] = useState(true);

    useEffect(() => {

        const savedUser = getUser();

        if (savedUser) {

            setUser(savedUser);

        }

        setLoading(false);

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

    return (

        <AuthContext.Provider

            value={{
                user,
                loading,
                login,
                register,
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