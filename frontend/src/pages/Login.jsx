import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function Login() {

    const navigate = useNavigate();

    const { user, login } = useAuth();

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    if (user) {
        return <Navigate to="/" replace />;
    }

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

        <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.16),_transparent_35%),linear-gradient(135deg,_#0a0f0d,_#111827_45%,_#050816)] px-4 text-white">

            <form
                onSubmit={handleSubmit}
                className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl"
            >

                <p className="mb-2 text-sm uppercase tracking-[0.35em] text-green-300/80">
                    TechStore AI
                </p>

                <h1 className="mb-2 text-4xl font-bold">

                    Login

                </h1>

                <p className="mb-8 text-sm text-neutral-300">
                    Sign in to manage chats, orders, and your profile.
                </p>

                <input
                    className="mb-4 w-full rounded-2xl border border-white/10 bg-black/30 p-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <input
                    type="password"
                    className="mb-6 w-full rounded-2xl border border-white/10 bg-black/30 p-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button
                    className="w-full rounded-2xl bg-green-500 p-3 font-bold text-black transition hover:bg-green-400"
                >
                    Login
                </button>

                <p className="mt-6 text-center text-sm text-neutral-300">
                    Don&apos;t have an account?{" "}
                    <Link
                        to="/register"
                        className="font-semibold text-green-300 hover:underline"
                    >
                        Create one
                    </Link>
                </p>

            </form>

        </div>

    );
}