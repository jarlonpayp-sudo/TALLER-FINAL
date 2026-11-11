import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Alert from "../components/Alert";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icons";
import Modal from "../components/Modal";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import StatCard from "../components/StatCard";
import { dateTime, money, number } from "../utils";

export default function Ventas() {
  const [ventas, setVentas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedSale, setSelectedSale] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  const loadVentas = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.ventas.listar(100);
      setVentas(data.ventas || []);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVentas();
  }, []);

  const completadas = ventas.filter((venta) => venta.estado === "COMPLETADA");
  const ingresos = completadas.reduce(
    (sum, venta) => sum + number(venta.total),
    0
  );
  const ticketPromedio = completadas.length
    ? ingresos / completadas.length
    : 0;

  const detailItems = selectedSale?.items || [];
  const detailTotal = useMemo(
    () => detailItems.reduce((sum, item) => sum + number(item.subtotal), 0),
    [detailItems]
  );

  const openDetail = async (venta) => {
    setDetailLoading(true);
    setDetailError("");
    setSelectedSale({ ...venta, items: [] });

    try {
      const data = await api.ventas.obtener(venta.id);
      setSelectedSale(data);
    } catch (requestError) {
      setDetailError(requestError.message);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedSale(null);
    setDetailError("");
  };

  return (
    <>
      <PageHeader
        eyebrow="Facturación"
        title="Ventas"
        description="Consulte las facturas registradas y revise el detalle de cada venta."
        actions={
          <Link to="/ventas/nueva" className="btn btn-primary">
            <Icon name="plus" size={17} />
            Nueva venta
          </Link>
        }
      />

      {error && (
        <Alert tone="danger" onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Spinner label="Cargando ventas..." />
      ) : (
        <>
          <div className="stat-grid stat-grid-3">
            <StatCard
              label="Ventas registradas"
              value={ventas.length}
              hint="En el historial"
              icon="receipt"
            />
            <StatCard
              label="Ingresos"
              value={money(ingresos)}
              hint="Solo ventas completadas"
              icon="money"
            />
            <StatCard
              label="Ticket promedio"
              value={money(ticketPromedio)}
              hint="Promedio por factura"
              icon="cart"
            />
          </div>

          <section className="card">
            <div className="card-header">
              <div>
                <h2>Historial de ventas</h2>
                <p>Últimas facturas registradas en el sistema.</p>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={loadVentas}
              >
                <Icon name="refresh" size={16} />
                Actualizar
              </button>
            </div>

            {ventas.length === 0 ? (
              <EmptyState
                icon="receipt"
                title="Aún no hay ventas registradas"
                description="Registre la primera venta para verla en este historial."
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
                      <th>Vendedor</th>
                      <th>Total</th>
                      <th>Estado</th>
                      <th className="actions-column">Detalle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ventas.map((venta) => (
                      <tr key={venta.id}>
                        <td>
                          <strong>{venta.numero_factura}</strong>
                          <small>Venta #{venta.id}</small>
                        </td>
                        <td>{dateTime(venta.created_at)}</td>
                        <td>{venta.vendedor_nombre || "—"}</td>
                        <td className="money">{money(venta.total)}</td>
                        <td>
                          <span
                            className={`badge ${
                              venta.estado === "ANULADA"
                                ? "badge-danger"
                                : "badge-success"
                            }`}
                          >
                            {venta.estado}
                          </span>
                        </td>
                        <td className="actions-column">
                          <button
                            type="button"
                            className="btn btn-ghost btn-sm"
                            onClick={() => openDetail(venta)}
                          >
                            Ver detalle
                            <Icon name="arrowRight" size={15} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}

      <Modal
        open={Boolean(selectedSale)}
        title={selectedSale ? `Factura ${selectedSale.numero_factura}` : "Detalle de venta"}
        subtitle="Resumen de la venta y productos facturados."
        onClose={closeDetail}
        size="lg"
      >
        {detailError && <Alert tone="danger">{detailError}</Alert>}
        {detailLoading ? (
          <Spinner label="Cargando detalle de la venta..." />
        ) : selectedSale ? (
          <>
            <div className="detail-grid">
              <div>
                <span>Vendedor</span>
                <strong>{selectedSale.vendedor_nombre || "—"}</strong>
              </div>
              <div>
                <span>Fecha</span>
                <strong>{dateTime(selectedSale.created_at)}</strong>
              </div>
              <div>
                <span>Estado</span>
                <strong>{selectedSale.estado}</strong>
              </div>
              <div>
                <span>Total</span>
                <strong>{money(selectedSale.total)}</strong>
              </div>
            </div>

            {selectedSale.notas && (
              <p className="detail-note">
                <strong>Notas:</strong> {selectedSale.notas}
              </p>
            )}

            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {detailItems.map((item) => (
                    <tr key={`${item.id}-${item.repuesto_id}`}>
                      <td>
                        <strong>{item.nombre}</strong>
                        <small>{item.codigo_referencia}</small>
                      </td>
                      <td>{item.cantidad}</td>
                      <td className="money">{money(item.precio_unitario)}</td>
                      <td className="money">{money(item.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="detail-total">
              <span>Total facturado</span>
              <strong>{money(detailTotal || selectedSale.total)}</strong>
            </div>
          </>
        ) : null}
      </Modal>
    </>
  );
}
