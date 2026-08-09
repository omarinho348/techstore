import { useEffect, useState } from "react";
import MainLayout from "../layouts/MainLayout";
import { getOrders } from "../api/orderApi";
import { getUser } from "../utils/storage";

export default function Orders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        async function load() {
            try {
                const data = await getOrders();

                if (mounted) setOrders(data || []);
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

    // Filter orders for current user if authenticated
    const myOrders = user
        ? orders.filter((o) => o.customer_id === user.customer_id)
        : [];

    return (
        <MainLayout>
            <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-4xl font-extrabold">My Orders</h1>
                        <p className="text-gray-500 mt-1">A quick summary of your recent purchases.</p>
                    </div>
                </div>

                {loading ? (
                    <div className="py-20 text-center text-gray-500">Loading orders…</div>
                ) : !user ? (
                    <div className="py-20 text-center text-gray-600">Please log in to see your orders.</div>
                ) : myOrders.length === 0 ? (
                    <div className="py-20 text-center text-gray-600">No orders found for your account.</div>
                ) : (
                    <div className="space-y-4">
                        {myOrders.map((order) => (
                            <div key={order.id} className="bg-gray-800 rounded-xl shadow p-4 text-white">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-sm text-gray-300">Order ID: {order.id}</div>
                                        <div className="text-lg font-semibold">{order.items.map(i => i.product_name).join(', ')}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xl font-bold">${order.total.toFixed(2)}</div>
                                        <div className={`text-sm font-medium px-2 py-1 rounded ${order.status === 'processing' ? 'bg-yellow-400 text-black' : order.status === 'shipped' ? 'bg-blue-600 text-white' : order.status === 'delivered' ? 'bg-green-600 text-white' : 'bg-gray-600 text-white'}`}>
                                            {order.status}
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="md:col-span-2">
                                        <table className="w-full text-sm text-gray-200">
                                            <thead className="text-left text-gray-300 text-xs uppercase">
                                                <tr>
                                                    <th>Product</th>
                                                    <th className="pl-6">Quantity</th>
                                                    <th className="pl-6">Unit Price</th>
                                                    <th className="pl-6">Subtotal</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {order.items.map((it) => (
                                                    <tr key={it.product_id} className="border-t border-gray-700">
                                                        <td className="py-2">{it.product_name}</td>
                                                        <td className="py-2 pl-6">{it.quantity}</td>
                                                        <td className="py-2 pl-6">${it.unit_price.toFixed(2)}</td>
                                                        <td className="py-2 pl-6">${(it.subtotal).toFixed(2)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    <div className="bg-gray-700 rounded p-3 text-gray-200">
                                        <div className="text-xs text-gray-300">Placed</div>
                                        <div className="text-sm">{new Date(order.created_at).toLocaleString()}</div>
                                        <div className="mt-3 text-xs text-gray-300">Updated</div>
                                        <div className="text-sm">{new Date(order.updated_at).toLocaleString()}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}