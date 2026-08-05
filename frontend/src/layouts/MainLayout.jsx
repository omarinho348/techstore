import Sidebar from "../components/Sidebar";

export default function MainLayout({ children }) {
    return (
        <div className="flex h-screen bg-[#212121] text-white">

            <Sidebar />

            <main className="flex-1 overflow-hidden">
                {children}
            </main>

        </div>
    );
}