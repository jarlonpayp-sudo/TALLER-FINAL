import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Alert from "../components/Alert";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icons";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import StatCard from "../components/StatCard";
import { useAuth } from "../context/AuthContext";
import { dateTime, money, number, stockState } from "../utils";

export default function Dashboard() {
  const { user } = useAuth();
  const [productos, setProductos] = useState(null);
  const [alertas, setAlertas] = useState(null);
  const [ventas, setVentas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      const results = await Promise.allSettled([
        api.productos.listar(),
        api.inventario.alertas(),
        api.ventas.listar(50),
      ]);

      if (!active) return;

      const [productosResult, alertasResult, ventasResult] = results;

      if (productosResult.status === "fulfilled") {
        setProductos(productosResult.value);
      }
      if (alertasResult.status === "fulfilled") {
        setAlertas(alertasResult.value);
      }
      if (ventasResult.status === "fulfilled") {
        setVentas(ventasResult.value);
      }

      const failed = results.find((result) => result.status === "rejected");
      if (failed) {
        setError(
          failed.reason?.message ||
            "Algunos datos no se pudieron cargar. Verifique el backend."
        );
      }

      setLoading(false);
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, []);

  const firstName = (user?.nombre || "equipo").split(" ")[0];
  const totalProductos = productos?.total ?? 0;
  const totalAlertas = alertas?.total_alertas ?? 0;
  const totalVentas = ventas?.total ?? 0;
  const ingresos = (ventas?.ventas || [])
    .filter((venta) => venta.estado === "COMPLETADA")
    .reduce((sum, venta) => sum + number(venta.total), 0);
  const alertasRecientes = (alertas?.productos_en_alerta || []).slice(0, 5);
  const ventasRecientes = (ventas?.ventas || []).slice(0, 5);

  return (
    <>
      <PageHeader
        eyebrow="Resumen general"
        title={`Hola, ${firstName}`}
        description="Este es el estado actual del catálogo, el inventario y las ventas."
        actions={
          <Link to="/productos" className="btn btn-secondary">
            <Icon name="box" size={17} />
            Ver catálogo
          </Link>
        }
      />

      {error && (
        <Alert tone="danger" onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Spinner label="Cargando el panel principal..." />
      ) : (
        <>
          <div className="stat-grid">
            <StatCard
              label="Productos activos"
              value={totalProductos}
              hint="Disponibles en el catálogo"
              icon="box"
            />
            <StatCard
              label="Alertas de stock"
              value={totalAlertas}
              hint="Requieren reposición"
              icon="alert"
              tone={totalAlertas > 0 ? "warning" : "default"}
            />
            <StatCard
              label="Ventas registradas"
              value={totalVentas}
              hint="En el historial reciente"
              icon="receipt"
            />
            <StatCard
              label="Ingresos recientes"
              value={money(ingresos)}
              hint="Ventas completadas"
              icon="money"
            />
          </div>

          <div className="dashboard-grid">
            <section className="card">
              <div className="card-header">
                <div>
                  <h2>Alertas de inventario</h2>
                  <p>Productos que necesitan reposición.</p>
                </div>
                <Link to="/inventario" className="text-link">
                  Ver todas
                  <Icon name="arrowRight" size={15} />
                </Link>
              </div>

              {alertasRecientes.length === 0 ? (
                <EmptyState
                  icon="check"
                  title="Sin alertas por ahora"
                  description="Todos los productos tienen existencias suficientes."
                />
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Repuesto</th>
                        <th>Stock</th>
                        <th>Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {alertasRecientes.map((producto) => {
                        const estado = stockState(producto);
                        return (
                          <tr key={producto.id}>
                            <td>
                              <strong>{producto.nombre}</strong>
                              <small>{producto.codigo_referencia}</small>
                            </td>
                            <td>
                              {producto.stock_actual} / {producto.stock_minimo}
                            </td>
                            <td>
                              <span className={`badge badge-${estado.tone}`}>
                                {producto.nivel_alerta === "AGOTADO"
                                  ? "Agotado"
                                  : "Stock bajo"}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="card">
              <div className="card-header">
                <div>
                  <h2>Ventas recientes</h2>
                  <p>Últimos movimientos registrados.</p>
                </div>
                <Link to="/ventas" className="text-link">
                  Ver historial
                  <Icon name="arrowRight" size={15} />
                </Link>
              </div>

              {ventasRecientes.length === 0 ? (
                <EmptyState
                  icon="receipt"
                  title="Aún no hay ventas"
                  description="Registre la primera venta desde el módulo de ventas."
                  action={
                    <Link to="/ventas/nueva" className="btn btn-primary btn-sm">
                      <Icon name="plus" size={16} />
                      Registrar venta
                    </Link>
                  }
                />
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Factura</th>
                        <th>Fecha</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ventasRecientes.map((venta) => (
                        <tr key={venta.id}>
                          <td>
                            <strong>{venta.numero_factura}</strong>
                            <small>{venta.vendedor_nombre}</small>
                          </td>
                          <td>{dateTime(venta.created_at)}</td>
                          <td className="money">{money(venta.total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>

          <div className="quick-grid">
            <Link to="/ventas/nueva" className="quick-card">
              <span className="quick-icon">
                <Icon name="cart" size={22} />
              </span>
              <span>
                <strong>Registrar una venta</strong>
                <small>Seleccione productos y genere la factura.</small>
              </span>
              <Icon name="arrowRight" size={18} />
            </Link>

            <Link to="/inventario" className="quick-card">
              <span className="quick-icon">
                <Icon name="layers" size={22} />
              </span>
              <span>
                <strong>Ajustar inventario</strong>
                <small>Registre entradas, salidas o correcciones.</small>
              </span>
              <Icon name="arrowRight" size={18} />
            </Link>

            <Link to="/productos" className="quick-card">
              <span className="quick-icon">
                <Icon name="box" size={22} />
              </span>
              <span>
                <strong>Administrar productos</strong>
                <small>Cree, edite o desactive repuestos.</small>
              </span>
              <Icon name="arrowRight" size={18} />
            </Link>
          </div>
        </>
      )}
    </>
  );
}
