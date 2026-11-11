import { useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { initials, longDate } from "../utils";
import Icon from "./Icons";

const navigation = [
  { to: "/", label: "Panel principal", icon: "grid", end: true },
  { to: "/productos", label: "Productos", icon: "box" },
  { to: "/inventario", label: "Inventario", icon: "layers" },
  { to: "/ventas", label: "Ventas", icon: "receipt" },
  { to: "/usuarios", label: "Usuarios", icon: "users", adminOnly: true },
];

const titles = [
  { prefix: "/ventas/nueva", title: "Nueva venta" },
  { prefix: "/ventas", title: "Ventas" },
  { prefix: "/productos", title: "Productos" },
  { prefix: "/inventario", title: "Inventario" },
  { prefix: "/usuarios", title: "Usuarios" },
  { prefix: "/", title: "Panel principal" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const currentTitle =
    titles.find((item) => location.pathname === item.prefix)?.title ||
    titles.find(
      (item) => item.prefix !== "/" && location.pathname.startsWith(item.prefix)
    )?.title ||
    "Panel principal";

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <div
        className={`sidebar-overlay ${menuOpen ? "is-visible" : ""}`}
        onClick={() => setMenuOpen(false)}
        aria-hidden="true"
      />

      <aside className={`sidebar ${menuOpen ? "is-open" : ""}`}>
        <div className="brand">
          <span className="brand-mark">AQ</span>
          <span className="brand-copy">
            <strong>AllQuality</strong>
            <small>Gestión de repuestos</small>
          </span>
        </div>

        <nav className="main-nav" aria-label="Navegación principal">
          <span className="nav-caption">Menú</span>
          {navigation
            .filter((item) => !item.adminOnly || user?.rol === "ADMIN")
            .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `nav-link ${isActive ? "is-active" : ""}`
              }
              onClick={() => setMenuOpen(false)}
            >
              <Icon name={item.icon} size={19} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <span className="avatar">{initials(user?.nombre)}</span>
            <span className="sidebar-user-copy">
              <strong>{user?.nombre || "Usuario"}</strong>
              <small>{user?.rol || "SIN ROL"}</small>
            </span>
          </div>
          <button type="button" className="logout-button" onClick={handleLogout}>
            <Icon name="logout" size={18} />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <button
            type="button"
            className="icon-button mobile-menu"
            onClick={() => setMenuOpen(true)}
            aria-label="Abrir menú"
          >
            <Icon name="menu" size={21} />
          </button>

          <div className="topbar-title">
            <span>AllQuality</span>
            <h1>{currentTitle}</h1>
          </div>

          <div className="topbar-actions">
            <span className="topbar-date">
              <Icon name="calendar" size={16} />
              {longDate()}
            </span>
            <Link to="/ventas/nueva" className="btn btn-primary btn-sm">
              <Icon name="plus" size={16} />
              Nueva venta
            </Link>
          </div>
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
