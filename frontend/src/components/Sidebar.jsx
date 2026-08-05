import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useConversations } from "../contexts/ConversationContext";

export default function Sidebar() {
    const { user, logout } = useAuth();

    const {
        conversations,
        newConversation,
        deleteConversation,
        setCurrentSessionId,
    } = useConversations();

    const navigate = useNavigate();

    function handleLogout() {
        logout();
        navigate("/login");
    }

    return (
        <aside className="flex h-screen w-72 flex-col bg-[#171717] p-4 text-white">

            <h1 className="mb-6 text-2xl font-bold">
                TechStore AI
            </h1>

            <button
                onClick={newConversation}
                className="mb-6 w-full rounded-lg bg-neutral-800 p-3 text-left transition hover:bg-neutral-700"
            >
                + New Chat
            </button>

            <div className="mb-8 flex-1 overflow-y-auto">

                <h2 className="mb-3 text-sm uppercase text-neutral-400">
                    Recent Chats
                </h2>

                <div className="space-y-2">

                    {conversations.length === 0 ? (

                        <p className="text-sm text-neutral-500">
                            No conversations yet
                        </p>

                    ) : (

                        conversations.map((conversation) => (

    <div
        key={conversation.session_id}
        className="flex items-center gap-2"
    >

        <button

            onClick={() =>
                setCurrentSessionId(
                    conversation.session_id
                )
            }

            className="flex-1 rounded-lg p-2 text-left transition hover:bg-neutral-800"

        >

            {conversation.title}

        </button>

        <button

            onClick={() =>
                deleteConversation(
                    conversation.session_id
                )
            }

            className="rounded-lg p-2 text-red-400 hover:bg-neutral-800"

            title="Delete conversation"

        >

            🗑

        </button>

    </div>

))

                    )}

                </div>

            </div>

            <nav className="mb-6 flex flex-col gap-2">

                <Link
                    to="/"
                    className="rounded-lg p-2 hover:bg-neutral-800"
                >
                    💬 Chat
                </Link>

                <Link
                    to="/orders"
                    className="rounded-lg p-2 hover:bg-neutral-800"
                >
                    📦 Orders
                </Link>

                <Link
                    to="/tickets"
                    className="rounded-lg p-2 hover:bg-neutral-800"
                >
                    🎫 Tickets
                </Link>

                <Link
                    to="/products"
                    className="rounded-lg p-2 hover:bg-neutral-800"
                >
                    🛍 Products
                </Link>

                <Link
                    to="/profile"
                    className="rounded-lg p-2 hover:bg-neutral-800"
                >
                    👤 Profile
                </Link>

            </nav>

            <hr className="mb-4 border-neutral-700" />

            <div>

                <p className="font-semibold">
                    {user?.name}
                </p>

                <p className="mb-4 text-sm text-neutral-400">
                    {user?.email}
                </p>

                <button
                    onClick={handleLogout}
                    className="w-full rounded-lg bg-red-600 p-3 transition hover:bg-red-500"
                >
                    Logout
                </button>

            </div>

        </aside>
    );
}