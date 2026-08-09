import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function Register() {

    const navigate = useNavigate();

    const { user, register } = useAuth();

    const [name, setName] = useState("");

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    if (user) {
        return <Navigate to="/" replace />;
    }

    async function handleSubmit(e) {

        e.preventDefault();

        try {

            await register({
                name,
                email,
                password,
            });

            navigate("/");

        } catch (err) {

            alert(err.response?.data?.detail || "Registration failed");

        }

    }

    return (

        <div className="flex h-screen items-center justify-center bg-neutral-900">

            <form
                onSubmit={handleSubmit}
                className="w-96 rounded-xl bg-neutral-800 p-8 shadow-xl"
            >

                <h1 className="mb-6 text-3xl font-bold">

                    Create Account

                </h1>

                <input
                    className="mb-4 w-full rounded border border-neutral-600 bg-neutral-900 p-3"
                    placeholder="Full Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />

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
                    className="w-full rounded bg-green-600 p-3 font-bold transition hover:bg-green-500"
                >
                    Register
                </button>

                <p className="mt-6 text-center text-sm text-neutral-400">

                    Already have an account?

                    {" "}

                    <Link
                        to="/login"
                        className="text-green-400 hover:underline"
                    >
                        Login
                    </Link>

                </p>

            </form>

        </div>

    );

}