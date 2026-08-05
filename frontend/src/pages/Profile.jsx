import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";

import { useAuth } from "../contexts/AuthContext";

function formatDate(value) {

    if (!value) {
        return "Not available";
    }

    return new Date(value).toLocaleString();

}

export default function Profile() {

    const navigate = useNavigate();

    const { user, updateProfile, logout } = useAuth();

    const [form, setForm] = useState({
        name: "",
        email: "",
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
    });

    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");

    const [success, setSuccess] = useState("");

    useEffect(() => {

        if (!user) {
            return;
        }

        setForm({
            name: user.name ?? "",
            email: user.email ?? "",
            currentPassword: "",
            newPassword: "",
            confirmPassword: "",
        });

    }, [user]);

    async function handleSubmit(event) {

        event.preventDefault();

        setError("");
        setSuccess("");

        const payload = {};

        const trimmedName = form.name.trim();
        const trimmedEmail = form.email.trim();

        if (trimmedName && trimmedName !== user?.name) {
            payload.name = trimmedName;
        }

        if (trimmedEmail && trimmedEmail !== user?.email) {
            payload.email = trimmedEmail;
        }

        const wantsPasswordChange =
            form.currentPassword || form.newPassword || form.confirmPassword;

        if (wantsPasswordChange) {

            if (!form.currentPassword || !form.newPassword) {
                setError("Provide your current password and a new password.");
                return;
            }

            if (form.newPassword !== form.confirmPassword) {
                setError("New password and confirmation do not match.");
                return;
            }

            payload.current_password = form.currentPassword;
            payload.new_password = form.newPassword;

        }

        if (Object.keys(payload).length === 0) {
            setError("Update at least one field before saving.");
            return;
        }

        try {

            setSaving(true);

            await updateProfile(payload);

            setForm((previous) => ({
                ...previous,
                currentPassword: "",
                newPassword: "",
                confirmPassword: "",
            }));

            setSuccess("Profile updated successfully.");

        } catch (err) {

            setError(
                err.response?.data?.detail ||
                err.message ||
                "Failed to update profile"
            );

        } finally {

            setSaving(false);

        }

    }

    function handleLogout() {

        logout();
        navigate("/login");

    }

    return (

        <MainLayout>

            <div className="h-full overflow-y-auto bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.10),_transparent_30%),linear-gradient(180deg,_#121212_0%,_#0b0b0b_100%)] px-6 py-8 text-white lg:px-10">

                <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[1.1fr_0.9fr]">

                    <section className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl">

                        <p className="mb-2 text-sm uppercase tracking-[0.35em] text-green-300/80">
                            Account
                        </p>

                        <h1 className="text-4xl font-bold">
                            Profile
                        </h1>

                        <p className="mt-3 max-w-2xl text-sm leading-6 text-neutral-300">
                            Keep your account details current. Changes here update your saved profile across the app.
                        </p>

                        {error ? (
                            <div className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                                {error}
                            </div>
                        ) : null}

                        {success ? (
                            <div className="mt-6 rounded-2xl border border-green-500/30 bg-green-500/10 px-4 py-3 text-sm text-green-200">
                                {success}
                            </div>
                        ) : null}

                        <form onSubmit={handleSubmit} className="mt-8 space-y-5">

                            <div className="grid gap-4 md:grid-cols-2">

                                <label className="space-y-2 text-sm text-neutral-200">
                                    <span>Full name</span>
                                    <input
                                        className="w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                                        placeholder="Your name"
                                        value={form.name}
                                        onChange={(event) => setForm((previous) => ({
                                            ...previous,
                                            name: event.target.value,
                                        }))}
                                    />
                                </label>

                                <label className="space-y-2 text-sm text-neutral-200">
                                    <span>Email address</span>
                                    <input
                                        type="email"
                                        className="w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                                        placeholder="you@example.com"
                                        value={form.email}
                                        onChange={(event) => setForm((previous) => ({
                                            ...previous,
                                            email: event.target.value,
                                        }))}
                                    />
                                </label>

                            </div>

                            <div className="grid gap-4 md:grid-cols-3">

                                <label className="space-y-2 text-sm text-neutral-200">
                                    <span>Current password</span>
                                    <input
                                        type="password"
                                        className="w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                                        placeholder="Required for password changes"
                                        value={form.currentPassword}
                                        onChange={(event) => setForm((previous) => ({
                                            ...previous,
                                            currentPassword: event.target.value,
                                        }))}
                                    />
                                </label>

                                <label className="space-y-2 text-sm text-neutral-200">
                                    <span>New password</span>
                                    <input
                                        type="password"
                                        className="w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                                        placeholder="Leave blank to keep current password"
                                        value={form.newPassword}
                                        onChange={(event) => setForm((previous) => ({
                                            ...previous,
                                            newPassword: event.target.value,
                                        }))}
                                    />
                                </label>

                                <label className="space-y-2 text-sm text-neutral-200">
                                    <span>Confirm new password</span>
                                    <input
                                        type="password"
                                        className="w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-3 outline-none transition placeholder:text-neutral-500 focus:border-green-400"
                                        placeholder="Repeat the new password"
                                        value={form.confirmPassword}
                                        onChange={(event) => setForm((previous) => ({
                                            ...previous,
                                            confirmPassword: event.target.value,
                                        }))}
                                    />
                                </label>

                            </div>

                            <div className="flex flex-col gap-3 sm:flex-row">

                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="rounded-2xl bg-green-500 px-5 py-3 font-semibold text-black transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-70"
                                >
                                    {saving ? "Saving..." : "Save changes"}
                                </button>

                                <button
                                    type="button"
                                    onClick={handleLogout}
                                    className="rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-3 font-semibold text-red-100 transition hover:bg-red-500/20"
                                >
                                    Logout
                                </button>

                            </div>

                        </form>

                    </section>

                    <aside className="space-y-6">

                        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl">

                            <p className="text-sm uppercase tracking-[0.35em] text-green-300/80">
                                Details
                            </p>

                            <div className="mt-5 space-y-4 text-sm text-neutral-200">
                                <div>
                                    <p className="text-neutral-400">Customer ID</p>
                                    <p className="mt-1 break-all font-medium">{user?.customer_id ?? user?.id ?? "Not available"}</p>
                                </div>

                                <div>
                                    <p className="text-neutral-400">Name</p>
                                    <p className="mt-1 font-medium">{user?.name ?? "Not available"}</p>
                                </div>

                                <div>
                                    <p className="text-neutral-400">Email</p>
                                    <p className="mt-1 font-medium">{user?.email ?? "Not available"}</p>
                                </div>

                                <div>
                                    <p className="text-neutral-400">Created</p>
                                    <p className="mt-1 font-medium">{formatDate(user?.created_at)}</p>
                                </div>

                                <div>
                                    <p className="text-neutral-400">Last updated</p>
                                    <p className="mt-1 font-medium">{formatDate(user?.updated_at)}</p>
                                </div>
                            </div>

                        </div>

                        <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-green-500/15 to-emerald-500/5 p-6 text-sm text-neutral-200 shadow-2xl backdrop-blur-xl">
                            <p className="text-base font-semibold text-white">What you can do here</p>
                            <ul className="mt-4 space-y-3 leading-6">
                                <li>Update your name and email without losing your session.</li>
                                <li>Change your password with a current-password confirmation.</li>
                                <li>Log out from this page when you are done.</li>
                            </ul>
                        </div>

                    </aside>

                </div>

            </div>

        </MainLayout>

    );

}