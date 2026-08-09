import Sidebar from "../components/Sidebar";

export default function MainLayout({ children }) {
    return (
        <div className="flex h-screen bg-[#121212]">

            <Sidebar />

            <main className="flex-1 overflow-hidden text-gray-100">
                {children}
            </main>

        </div>
    );
}