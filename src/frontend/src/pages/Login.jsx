import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import Alert from "../components/Alert";
import Icon from "../components/Icons";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("vendedor@allquality.com");
  const [password, setPassword] = useState("Admin123*");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email.trim(), password);
      const destination = location.state?.from?.pathname || "/";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <section className="login-brand-panel">
        <div className="brand brand-inverse">
          <span className="brand-mark">AQ</span>
          <span className="brand-copy">
            <strong>AllQuality</strong>
            <small>Gestión de repuestos</small>
          </span>
        </div>

        <div className="login-brand-content">
          <span className="eyebrow light">Control comercial</span>
          <h1>Todo el inventario y las ventas en un solo lugar.</h1>
          <p>
            Administre el catálogo, controle las existencias y registre cada
            venta con trazabilidad completa.
          </p>

          <ul className="login-features">
            <li>
              <span className="feature-check">
                <Icon name="check" size={14} />
              </span>
              Control de stock en tiempo real
            </li>
            <li>
              <span className="feature-check">
                <Icon name="check" size={14} />
              </span>
              Alertas de reposición automáticas
            </li>
            <li>
              <span className="feature-check">
                <Icon name="check" size={14} />
              </span>
              Facturación con auditoría de movimientos
            </li>
          </ul>
        </div>

        <p className="login-copyright">
          COTECNOVA · Ingeniería de Software II · 2026-2
        </p>
      </section>

      <section className="login-form-panel">
        <div className="login-card">
          <span className="eyebrow">Bienvenido</span>
          <h2>Iniciar sesión</h2>
          <p className="muted">
            Ingrese con su cuenta para administrar el catálogo, el inventario y
            las ventas.
          </p>

          {error && (
            <Alert tone="danger" onClose={() => setError("")}>
              {error}
            </Alert>
          )}

          <form className="form-stack" onSubmit={handleSubmit}>
            <label className="field">
              <span>Correo electrónico</span>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="usuario@allquality.com"
                autoComplete="username"
                required
              />
            </label>

            <label className="field">
              <span>Contraseña</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Ingrese su contraseña"
                autoComplete="current-password"
                required
              />
            </label>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={loading}
            >
              {loading ? "Ingresando..." : "Ingresar"}
              {!loading && <Icon name="arrowRight" size={18} />}
            </button>
          </form>

          <div className="demo-box">
            <strong>Credenciales de demostración</strong>
            <span>vendedor@allquality.com · Admin123*</span>
            <span>admin@allquality.com · Admin123*</span>
          </div>
        </div>
      </section>
    </div>
  );
}
