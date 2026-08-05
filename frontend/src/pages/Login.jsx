import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function Login() {

    const navigate = useNavigate();

    const { user, login } = useAuth();

    if (user) {
    return <Navigate to="/" replace />;
}

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    async function handleSubmit(e) {

        e.preventDefault();

        try {

            await login({
                email,
                password,
            });

            navigate("/");

        } catch (err) {

            console.log(err);

alert(
    JSON.stringify(err.response?.data) ||
    err.message ||
    "Login failed"
);

        }

    }

    return (

        <div className="flex h-screen items-center justify-center bg-neutral-900">

            <form
                onSubmit={handleSubmit}
                className="w-96 rounded-xl bg-neutral-800 p-8"
            >

                <h1 className="mb-6 text-3xl font-bold">

                    Login

                </h1>

                <input
                    className="mb-4 w-full rounded border border-neutral-600 bg-neutral-900 p-3"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <input
                    type="password"
                    className="mb-6 w-full rounded border border-neutral-600 bg-neutral-900 p-3"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button
                    className="w-full rounded bg-green-500 p-3 font-bold"
                >
                    Login
                </button>

            </form>

        </div>

    );


    <p className="mt-6 text-center text-sm text-neutral-400">
    Don't have an account?{" "}
    <Link
        to="/register"
        className="text-green-400 hover:underline"
    >
        Register
    </Link>
</p>
}