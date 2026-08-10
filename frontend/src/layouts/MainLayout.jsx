import Sidebar from "../components/Sidebar";

export default function MainLayout({ children }) {
    return (
        <div className="flex h-screen bg-[#121212]">

            <Sidebar />

            <main className="flex-1 min-w-0 overflow-x-hidden overflow-y-auto text-gray-100">
                {children}
            </main>

        </div>
    );
}
