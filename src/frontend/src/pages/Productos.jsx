import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import Alert from "../components/Alert";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icons";
import Modal from "../components/Modal";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";
import { money, number, stockState } from "../utils";

const emptyForm = {
  categoria_id: "",
  codigo_referencia: "",
  codigo_oem: "",
  nombre: "",
  marca_moto: "",
  precio_compra: "",
  precio_venta: "",
  stock_actual: "0",
  stock_minimo: "3",
};

export default function Productos() {
  const { user } = useAuth();
  const canManage = user?.rol === "ADMIN" || user?.rol === "INVENTARIO";

  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [refresh, setRefresh] = useState(0);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    api.categorias
      .listar()
      .then((data) => {
        if (active) setCategorias(data.categorias || []);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    const timer = window.setTimeout(async () => {
      setLoading(true);
      setError("");

      try {
        const data = await api.productos.listar({ q, cat });
        if (active) setProductos(data.productos || []);
      } catch (requestError) {
        if (active) setError(requestError.message);
      } finally {
        if (active) setLoading(false);
      }
    }, 250);

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [q, cat, refresh]);

  const categoriaMap = useMemo(
    () => new Map(categorias.map((categoria) => [categoria.id, categoria.nombre])),
    [categorias]
  );

  const openCreate = () => {
    setEditing(null);
    setForm({
      ...emptyForm,
      categoria_id: categorias[0]?.id ? String(categorias[0].id) : "",
    });
    setFormError("");
    setModalOpen(true);
  };

  const openEdit = (producto) => {
    setEditing(producto);
    setForm({
      categoria_id: String(producto.categoria_id),
      codigo_referencia: producto.codigo_referencia || "",
      codigo_oem: producto.codigo_oem || "",
      nombre: producto.nombre || "",
      marca_moto: producto.marca_moto || "",
      precio_compra: String(number(producto.precio_compra)),
      precio_venta: String(number(producto.precio_venta)),
      stock_actual: String(number(producto.stock_actual)),
      stock_minimo: String(number(producto.stock_minimo)),
    });
    setFormError("");
    setModalOpen(true);
  };

  const updateField = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError("");

    if (!form.categoria_id || !form.codigo_referencia.trim() || !form.nombre.trim()) {
      setFormError("Categoría, código y nombre son obligatorios.");
      return;
    }

    const precioVenta = Number(form.precio_venta);
    if (!Number.isFinite(precioVenta) || precioVenta <= 0) {
      setFormError("El precio de venta debe ser mayor que cero.");
      return;
    }

    const payload = {
      categoria_id: Number(form.categoria_id),
      codigo_referencia: form.codigo_referencia.trim(),
      codigo_oem: form.codigo_oem.trim(),
      nombre: form.nombre.trim(),
      marca_moto: form.marca_moto.trim(),
      precio_compra: Number(form.precio_compra || 0),
      precio_venta: precioVenta,
      stock_minimo: Number(form.stock_minimo || 0),
    };

    setSaving(true);
    try {
      if (editing) {
        await api.productos.actualizar(editing.id, payload);
        setNotice("Repuesto actualizado correctamente.");
      } else {
        await api.productos.crear({
          ...payload,
          stock_actual: Number(form.stock_actual || 0),
        });
        setNotice("Repuesto registrado correctamente.");
      }
      setModalOpen(false);
      setRefresh((value) => value + 1);
    } catch (requestError) {
      setFormError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (producto) => {
    const confirmed = window.confirm(
      `¿Desactivar "${producto.nombre}"? Dejará de aparecer en el catálogo, pero conservará su historial.`
    );
    if (!confirmed) return;

    try {
      await api.productos.desactivar(producto.id);
      setNotice("Repuesto desactivado correctamente.");
      setRefresh((value) => value + 1);
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Catálogo"
        title="Productos"
        description="Consulte, registre y mantenga los repuestos disponibles en el negocio."
        actions={
          canManage ? (
            <button type="button" className="btn btn-primary" onClick={openCreate}>
              <Icon name="plus" size={17} />
              Nuevo repuesto
            </button>
          ) : null
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

      <section className="card">
        <div className="toolbar">
          <label className="search-field">
            <Icon name="search" size={18} />
            <input
              type="search"
              value={q}
              onChange={(event) => setQ(event.target.value)}
              placeholder="Buscar por nombre, referencia u OEM..."
              aria-label="Buscar repuestos"
            />
          </label>

          <select
            className="select toolbar-select"
            value={cat}
            onChange={(event) => setCat(event.target.value)}
            aria-label="Filtrar por categoría"
          >
            <option value="">Todas las categorías</option>
            {categorias.map((categoria) => (
              <option key={categoria.id} value={categoria.id}>
                {categoria.nombre}
              </option>
            ))}
          </select>

          {(q || cat) && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setQ("");
                setCat("");
              }}
            >
              Limpiar
            </button>
          )}
        </div>

        {loading ? (
          <Spinner label="Cargando repuestos..." />
        ) : productos.length === 0 ? (
          <EmptyState
            icon="box"
            title="No se encontraron repuestos"
            description={
              q || cat
                ? "Pruebe con otra búsqueda o quite los filtros."
                : "El catálogo está vacío. Registre el primer repuesto."
            }
            action={
              canManage ? (
                <button type="button" className="btn btn-primary btn-sm" onClick={openCreate}>
                  <Icon name="plus" size={16} />
                  Nuevo repuesto
                </button>
              ) : null
            }
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Repuesto</th>
                  <th>Categoría</th>
                  <th>Precio venta</th>
                  <th>Stock</th>
                  <th>Estado</th>
                  {canManage && <th className="actions-column">Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {productos.map((producto) => {
                  const estado = stockState(producto);
                  return (
                    <tr key={producto.id}>
                      <td>
                        <strong>{producto.nombre}</strong>
                        <small>
                          {producto.codigo_referencia}
                          {producto.codigo_oem ? ` · OEM ${producto.codigo_oem}` : ""}
                        </small>
                      </td>
                      <td>
                        {producto.categoria_nombre ||
                          categoriaMap.get(producto.categoria_id) ||
                          "—"}
                      </td>
                      <td className="money">{money(producto.precio_venta)}</td>
                      <td>
                        <strong>{producto.stock_actual}</strong>
                        <small>mín. {producto.stock_minimo}</small>
                      </td>
                      <td>
                        <span className={`badge badge-${estado.tone}`}>
                          {estado.label}
                        </span>
                      </td>
                      {canManage && (
                        <td className="actions-column">
                          <div className="row-actions">
                            <button
                              type="button"
                              className="icon-button"
                              onClick={() => openEdit(producto)}
                              title="Editar repuesto"
                              aria-label={`Editar ${producto.nombre}`}
                            >
                              <Icon name="edit" size={17} />
                            </button>
                            <button
                              type="button"
                              className="icon-button danger"
                              onClick={() => handleDeactivate(producto)}
                              title="Desactivar repuesto"
                              aria-label={`Desactivar ${producto.nombre}`}
                            >
                              <Icon name="trash" size={17} />
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal
        open={modalOpen}
        title={editing ? "Editar repuesto" : "Nuevo repuesto"}
        subtitle={
          editing
            ? "Actualice los datos del catálogo. El stock se modifica desde Inventario."
            : "Registre un nuevo producto en el catálogo."
        }
        onClose={() => setModalOpen(false)}
        size="lg"
      >
        {formError && <Alert tone="danger">{formError}</Alert>}

        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label className="field field-span-2">
              <span>Nombre del repuesto *</span>
              <input
                value={form.nombre}
                onChange={updateField("nombre")}
                placeholder="Ej. Pastillas de freno delanteras"
                required
              />
            </label>

            <label className="field">
              <span>Categoría *</span>
              <select
                value={form.categoria_id}
                onChange={updateField("categoria_id")}
                required
              >
                <option value="">Seleccione una categoría</option>
                {categorias.map((categoria) => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.nombre}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Código de referencia *</span>
              <input
                value={form.codigo_referencia}
                onChange={updateField("codigo_referencia")}
                placeholder="Ej. PAST-FR-FZ16"
                required
              />
            </label>

            <label className="field">
              <span>Código OEM</span>
              <input
                value={form.codigo_oem}
                onChange={updateField("codigo_oem")}
                placeholder="Código del fabricante"
              />
            </label>

            <label className="field">
              <span>Marca / moto compatible</span>
              <input
                value={form.marca_moto}
                onChange={updateField("marca_moto")}
                placeholder="Ej. Yamaha FZ16"
              />
            </label>

            <label className="field">
              <span>Precio de compra</span>
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.precio_compra}
                onChange={updateField("precio_compra")}
                placeholder="0"
              />
            </label>

            <label className="field">
              <span>Precio de venta *</span>
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={form.precio_venta}
                onChange={updateField("precio_venta")}
                placeholder="0"
                required
              />
            </label>

            {!editing && (
              <label className="field">
                <span>Stock inicial</span>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={form.stock_actual}
                  onChange={updateField("stock_actual")}
                />
              </label>
            )}

            <label className="field">
              <span>Stock mínimo</span>
              <input
                type="number"
                min="0"
                step="1"
                value={form.stock_minimo}
                onChange={updateField("stock_minimo")}
              />
            </label>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setModalOpen(false)}
            >
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving
                ? "Guardando..."
                : editing
                  ? "Guardar cambios"
                  : "Registrar repuesto"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
