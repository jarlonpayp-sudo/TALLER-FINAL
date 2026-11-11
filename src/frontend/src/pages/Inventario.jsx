import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import Alert from "../components/Alert";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icons";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import StatCard from "../components/StatCard";
import { useAuth } from "../context/AuthContext";
import { number } from "../utils";

const emptyForm = {
  repuesto_id: "",
  cantidad: "",
  tipo: "COMPRA",
  justificacion: "",
};

export default function Inventario() {
  const { user } = useAuth();
  const canAdjust = user?.rol === "ADMIN" || user?.rol === "INVENTARIO";

  const [alertas, setAlertas] = useState([]);
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [resultado, setResultado] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [alertasData, productosData] = await Promise.all([
        api.inventario.alertas(),
        api.productos.listar(),
      ]);
      setAlertas(alertasData.productos_en_alerta || []);
      setProductos(productosData.productos || []);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const agotados = useMemo(
    () => alertas.filter((producto) => number(producto.stock_actual) === 0).length,
    [alertas]
  );
  const stockBajo = alertas.length - agotados;

  const selectedProduct = productos.find(
    (producto) => String(producto.id) === String(form.repuesto_id)
  );
  const cantidad = Number(form.cantidad || 0);
  const stockPreview = selectedProduct
    ? number(selectedProduct.stock_actual) + cantidad
    : null;

  const updateField = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
    setResultado(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!form.repuesto_id) {
      setError("Seleccione un repuesto.");
      return;
    }
    if (!form.cantidad || !Number.isFinite(cantidad) || cantidad === 0) {
      setError("Ingrese una cantidad diferente de cero.");
      return;
    }
    if (stockPreview !== null && stockPreview < 0) {
      setError("El ajuste dejaría el stock en negativo.");
      return;
    }

    setSaving(true);
    try {
      const data = await api.inventario.ajustar({
        repuesto_id: Number(form.repuesto_id),
        cantidad,
        tipo: form.tipo,
        usuario_id: user?.id || 1,
        justificacion:
          form.justificacion.trim() ||
          (cantidad > 0 ? "Entrada manual de inventario" : "Salida manual de inventario"),
      });
      setResultado(data.resultado);
      setNotice("Inventario ajustado correctamente.");
      setForm((current) => ({ ...current, cantidad: "", justificacion: "" }));
      await loadData();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Bodega"
        title="Inventario"
        description="Consulte las alertas de stock y registre entradas o salidas de mercancía."
        actions={
          <button type="button" className="btn btn-secondary" onClick={loadData}>
            <Icon name="refresh" size={17} />
            Actualizar
          </button>
        }
      />

      {error && (
        <Alert tone="danger" onClose={() => setError("")}>
          {error}
        </Alert>
      )}
      {notice && (
        <Alert tone="success" onClose={() => setNotice("")}>
          {notice}
        </Alert>
      )}

      {loading ? (
        <Spinner label="Cargando inventario..." />
      ) : (
        <>
          <div className="stat-grid stat-grid-3">
            <StatCard
              label="Productos en alerta"
              value={alertas.length}
              hint="Requieren revisión"
              icon="alert"
              tone={alertas.length > 0 ? "warning" : "default"}
            />
            <StatCard
              label="Agotados"
              value={agotados}
              hint="Sin unidades disponibles"
              icon="box"
              tone={agotados > 0 ? "danger" : "default"}
            />
            <StatCard
              label="Stock bajo"
              value={stockBajo}
              hint="Por debajo del mínimo"
              icon="layers"
              tone={stockBajo > 0 ? "warning" : "default"}
            />
          </div>

          <div className="inventory-grid">
            <section className="card">
              <div className="card-header">
                <div>
                  <h2>Alertas de stock</h2>
                  <p>Productos con existencias iguales o menores al mínimo.</p>
                </div>
              </div>

              {alertas.length === 0 ? (
                <EmptyState
                  icon="check"
                  title="Todo el inventario está en orden"
                  description="No hay productos por debajo del stock mínimo."
                />
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Repuesto</th>
                        <th>Categoría</th>
                        <th>Stock</th>
                        <th>Alerta</th>
                      </tr>
                    </thead>
                    <tbody>
                      {alertas.map((producto) => (
                        <tr key={producto.id}>
                          <td>
                            <strong>{producto.nombre}</strong>
                            <small>{producto.codigo_referencia}</small>
                          </td>
                          <td>{producto.categoria_nombre}</td>
                          <td>
                            <strong>{producto.stock_actual}</strong>
                            <small>mín. {producto.stock_minimo}</small>
                          </td>
                          <td>
                            <span
                              className={`badge ${
                                producto.nivel_alerta === "AGOTADO"
                                  ? "badge-danger"
                                  : "badge-warning"
                              }`}
                            >
                              {producto.nivel_alerta === "AGOTADO"
                                ? "Agotado"
                                : "Stock bajo"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="card">
              <div className="card-header">
                <div>
                  <h2>Ajustar existencias</h2>
                  <p>Registre una entrada o una salida de bodega.</p>
                </div>
              </div>

              {!canAdjust ? (
                <EmptyState
                  icon="user"
                  title="Acceso de solo lectura"
                  description="Su rol permite consultar el inventario, pero no modificarlo."
                />
              ) : (
                <form className="form-stack" onSubmit={handleSubmit}>
                  <label className="field">
                    <span>Repuesto</span>
                    <select
                      value={form.repuesto_id}
                      onChange={updateField("repuesto_id")}
                      required
                    >
                      <option value="">Seleccione un repuesto</option>
                      {productos.map((producto) => (
                        <option key={producto.id} value={producto.id}>
                          {producto.nombre} ({producto.stock_actual} unidades)
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="form-grid">
                    <label className="field">
                      <span>Cantidad</span>
                      <input
                        type="number"
                        step="1"
                        value={form.cantidad}
                        onChange={updateField("cantidad")}
                        placeholder="Ej. 5 o -3"
                        required
                      />
                      <small className="field-hint">
                        Positiva para entrada, negativa para salida.
                      </small>
                    </label>

                    <label className="field">
                      <span>Tipo de movimiento</span>
                      <select value={form.tipo} onChange={updateField("tipo")}>
                        <option value="COMPRA">Compra / entrada</option>
                        <option value="AJUSTE">Ajuste de inventario</option>
                        <option value="VENTA">Salida por venta</option>
                        <option value="ANULACION">Anulación</option>
                      </select>
                    </label>
                  </div>

                  <label className="field">
                    <span>Justificación</span>
                    <textarea
                      rows="3"
                      value={form.justificacion}
                      onChange={updateField("justificacion")}
                      placeholder="Motivo del ajuste (opcional)"
                    />
                  </label>

                  {selectedProduct && (
                    <div className="stock-preview">
                      <span>Stock actual</span>
                      <strong>{selectedProduct.stock_actual}</strong>
                      <Icon name="arrowRight" size={16} />
                      <span>Nuevo stock</span>
                      <strong className={stockPreview < 0 ? "text-danger" : ""}>
                        {stockPreview}
                      </strong>
                    </div>
                  )}

                  {resultado && (
                    <Alert tone="success">
                      Ajuste aplicado: {resultado.stock_anterior} →{" "}
                      {resultado.stock_nuevo} unidades.
                    </Alert>
                  )}

                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={saving || productos.length === 0}
                  >
                    {saving ? "Aplicando..." : "Aplicar ajuste"}
                  </button>
                </form>
              )}
            </section>
          </div>
        </>
      )}
    </>
  );
}
