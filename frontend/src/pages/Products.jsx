import { useEffect, useState } from "react";
import MainLayout from "../layouts/MainLayout";
import { getProducts } from "../api/productApi";
import { getUser } from "../utils/storage";

export default function Products() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState("");

    useEffect(() => {
        let mounted = true;

        async function load() {
            try {
                const data = await getProducts();

                if (mounted) {
                    setProducts(data || []);
                }
            } catch (err) {
                console.error(err);
            } finally {
                if (mounted) setLoading(false);
            }
        }

        load();

        return () => (mounted = false);
    }, []);

    const filtered = products.filter((p) => {
        const q = query.trim().toLowerCase();
        if (!q) return true;
        return (
            p.name.toLowerCase().includes(q) ||
            p.category.toLowerCase().includes(q) ||
            p.description.toLowerCase().includes(q)
        );
    });

    const user = getUser();

    return (
        <MainLayout>
            <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-4xl font-extrabold">Products</h1>
                        <p className="text-gray-500 mt-1">
                            Browse TechStore's catalog. {user ? `Signed in as ${user.name}` : ""}
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <input
                            className="border rounded-lg px-4 py-2 w-72 focus:outline-none"
                            placeholder="Search products or categories..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                    </div>
                </div>

                {loading ? (
                    <div className="py-20 text-center text-gray-500">Loading products…</div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {filtered.map((p) => (
                            <div key={p.id} className="bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow">
                                <div className="p-4 text-white">
                                    <div className="flex items-start justify-between">
                                        <h2 className="text-lg font-semibold">{p.name}</h2>
                                        <span className={`text-sm font-medium px-2 py-1 rounded ${p.stock>0 ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}>
                                            {p.stock > 0 ? `In stock (${p.stock})` : 'Out of stock'}
                                        </span>
                                    </div>

                                    <p className="text-sm text-gray-300 mt-2 line-clamp-3">{p.description || 'No description available.'}</p>

                                    <div className="mt-4 flex items-center justify-between">
                                        <div>
                                            <div className="text-2xl font-bold text-emerald-300">${p.price.toFixed(2)}</div>
                                            <div className="text-xs text-gray-400">Category: {p.category || 'General'}</div>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <button className="px-3 py-1 bg-emerald-500 text-white rounded-md hover:bg-emerald-600">Details</button>
                                        </div>
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