import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import { AuthProvider } from "./context/AuthContext";
import Dashboard from "./pages/Dashboard";
import Inventario from "./pages/Inventario";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import NuevaVenta from "./pages/NuevaVenta";
import Productos from "./pages/Productos";
import Usuarios from "./pages/Usuarios";
import Ventas from "./pages/Ventas";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="productos" element={<Productos />} />
            <Route path="inventario" element={<Inventario />} />
            <Route path="ventas" element={<Ventas />} />
            <Route path="ventas/nueva" element={<NuevaVenta />} />
            <Route element={<RoleRoute roles={["ADMIN"]} />}>
              <Route path="usuarios" element={<Usuarios />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  );
}
