import { Routes, Route } from "react-router-dom";

import Login from "../pages/Login";
import Register from "../pages/Register";
import Chat from "../pages/Chat";
import Orders from "../pages/Orders";
import Products from "../pages/Products";
import Tickets from "../pages/Tickets";
import Profile from "../pages/Profile";
import NotFound from "../pages/NotFound";
import ProtectedRoute from "../components/ProtectedRoute";

export default function AppRoutes() {
    return (
        <Routes>

            <Route
    path="/"
    element={
        <ProtectedRoute>
            <Chat />
        </ProtectedRoute>
    }
/>

            <Route
                path="/login"
                element={<Login />}
            />

            <Route
                path="/register"
                element={<Register />}
            />

            <Route
    path="/orders"
    element={
        <ProtectedRoute>
            <Orders />
        </ProtectedRoute>
    }
/>

            <Route
    path="/products"
    element={
        <ProtectedRoute>
            <Products />
        </ProtectedRoute>
    }
/>

            <Route
    path="/tickets"
    element={
        <ProtectedRoute>
            <Tickets />
        </ProtectedRoute>
    }
/>

            <Route
    path="/profile"
    element={
        <ProtectedRoute>
            <Profile />
        </ProtectedRoute>
    }
/>

            <Route
                path="*"
                element={<NotFound />}
            />

        </Routes>
    );
}