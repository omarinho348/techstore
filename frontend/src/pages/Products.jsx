import { useEffect, useState } from "react";
import MainLayout from "../layouts/MainLayout";
import { getProducts, getRecommendedProducts } from "../api/productApi";
import { getUser } from "../utils/storage";

export default function Products() {
    const [products, setProducts] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [query, setQuery] = useState("");

    useEffect(() => {
        let mounted = true;

        async function load() {
            try {
                const user = getUser();
                const [productData, recommendationData] = await Promise.all([
                    getProducts(),
                    user ? getRecommendedProducts().catch(() => null) : Promise.resolve(null),
                ]);
                if (mounted) {
                    setProducts(productData || []);
                    setRecommendations(recommendationData?.recommendations || []);
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
        return !q || p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q) || p.description.toLowerCase().includes(q);
    });
    const user = getUser();

    return (
        <MainLayout>
            <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-4xl font-extrabold">Products</h1>
                        <p className="text-gray-500 mt-1">Browse TechStore's catalog. {user ? `Signed in as ${user.name}` : ""}</p>
                    </div>
                    <input className="border rounded-lg px-4 py-2 w-72 focus:outline-none" placeholder="Search products or categories..." value={query} onChange={(e) => setQuery(e.target.value)} />
                </div>

                {loading ? <div className="py-20 text-center text-gray-500">Loading products?</div> : (
                    <>
                        {recommendations.length > 0 && (
                            <section className="mb-10">
                                <h2 className="text-2xl font-bold">Recommended for you</h2>
                                <p className="text-gray-500 mt-1 mb-4">Picked from your previous orders and what is currently in stock.</p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                                    {recommendations.map((product) => <ProductCard key={product.id} product={product} recommended />)}
                                </div>
                            </section>
                        )}
                        <section>
                            <h2 className="text-2xl font-bold mb-4">All products</h2>
                            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                                {filtered.map((product) => <ProductCard key={product.id} product={product} />)}
                            </div>
                        </section>
                    </>
                )}
            </div>
        </MainLayout>
    );
}

function ProductCard({ product, recommended = false }) {
    return (
        <div className="bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow">
            <div className="p-4 text-white">
                <div className="flex items-start justify-between gap-2">
                    <div>
                        <h2 className="text-lg font-semibold">{product.name}</h2>
                        {recommended && <span className="text-xs text-emerald-300">Recommended for you</span>}
                    </div>
                    <span className={`text-sm font-medium px-2 py-1 rounded ${product.stock > 0 ? "bg-green-600" : "bg-red-600"}`}>
                        {product.stock > 0 ? `In stock (${product.stock})` : "Out of stock"}
                    </span>
                </div>
                <p className="text-sm text-gray-300 mt-2 line-clamp-3">{product.description || "No description available."}</p>
                {recommended && <p className="text-xs text-gray-400 mt-2">{product.reason}</p>}
                <div className="mt-4 flex items-center justify-between">
                    <div>
                        <div className="text-2xl font-bold text-emerald-300">${product.price.toFixed(2)}</div>
                        <div className="text-xs text-gray-400">Category: {product.category || "General"}</div>
                    </div>
                    <button className="px-3 py-1 bg-emerald-500 text-white rounded-md hover:bg-emerald-600">Details</button>
                </div>
            </div>
        </div>
    );
}
