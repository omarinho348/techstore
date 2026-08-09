import { useEffect, useState } from "react";
import MainLayout from "../layouts/MainLayout";
import { getTickets } from "../api/ticketApi";
import { getUser } from "../utils/storage";

export default function Tickets() {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        async function load() {
            try {
                const data = await getTickets();
                if (mounted) setTickets(data || []);
            } catch (err) {
                console.error(err);
            } finally {
                if (mounted) setLoading(false);
            }
        }

        load();

        return () => (mounted = false);
    }, []);

    const user = getUser();

    const myTickets = user
        ? tickets.filter((t) => t.customer_id === user.customer_id || t.customer_id === String(user.customer_id))
        : [];

    return (
        <MainLayout>
            <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-4xl font-extrabold">Support Tickets</h1>
                        <p className="text-gray-400 mt-1">Issues escalated to support and their current status.</p>
                    </div>
                </div>

                {loading ? (
                    <div className="py-20 text-center text-gray-500">Loading tickets…</div>
                ) : !user ? (
                    <div className="py-20 text-center text-gray-600">Please log in to see your tickets.</div>
                ) : myTickets.length === 0 ? (
                    <div className="py-20 text-center text-gray-600">No tickets found for your account.</div>
                ) : (
                    <div className="space-y-4">
                        {myTickets.map((t) => (
                            <div key={t.ticket_id} className="bg-gray-800 rounded-xl shadow p-4 text-white">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-sm text-gray-300">{t.ticket_id}</div>
                                        <div className="text-lg font-semibold">{t.subject}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-sm font-medium px-2 py-1 rounded ${t.status === 'open' ? 'bg-yellow-400 text-black' : t.status === 'in_progress' ? 'bg-blue-600 text-white' : t.status === 'resolved' ? 'bg-green-600 text-white' : 'bg-gray-600 text-white'}`}>
                                            {t.status}
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-3 text-gray-300">{t.description}</div>

                                <div className="mt-3 text-xs text-gray-400">Created: {new Date(t.created_at).toLocaleString()}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}