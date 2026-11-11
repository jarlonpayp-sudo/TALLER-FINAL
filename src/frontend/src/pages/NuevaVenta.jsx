import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import Alert from "../components/Alert";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icons";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";
import { money, number } from "../utils";

export default function NuevaVenta() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [productos, setProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [catFilter, setCatFilter] = useState("");
  const [cart, setCart] = useState([]);
  const [notas, setNotas] = useState("");
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    let active = true;

    async function loadData() {
      setLoading(true);
      setError("");
      try {
        const [productosData, categoriasData] = await Promise.all([
          api.productos.listar(),
          api.categorias.listar(),
        ]);
        if (!active) return;
        setProductos(productosData.productos || []);
        setCategorias(categoriasData.categorias || []);
      } catch (requestError) {
        if (active) setError(requestError.message);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadData();
    return () => {
      active = false;
    };
  }, []);

  const filteredProducts = useMemo(() => {
    const term = search.trim().toLowerCase();
    return [...productos]
      .filter((producto) => {
        const matchesCategory = catFilter
          ? String(producto.categoria_id) === catFilter
          : true;
        const matchesSearch = term
          ? [producto.nombre, producto.codigo_referencia, producto.codigo_oem]
              .filter(Boolean)
              .some((value) => value.toLowerCase().includes(term))
          : true;
        return matchesCategory && matchesSearch;
      })
      .sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
  }, [productos, search, catFilter]);

  const cartCount = cart.reduce((sum, item) => sum + item.cantidad, 0);
  const subtotal = cart.reduce(
    (sum, item) => sum + item.precio_unitario * item.cantidad,
    0
  );

  const quantityInCart = (repuestoId) =>
    cart.find((item) => item.repuesto_id === repuestoId)?.cantidad || 0;

  const addToCart = (producto) => {
    const stock = number(producto.stock_actual);
    if (stock <= 0) return;

    setCart((current) => {
      const existing = current.find((item) => item.repuesto_id === producto.id);
      if (existing) {
        if (existing.cantidad >= stock) return current;
        return current.map((item) =>
          item.repuesto_id === producto.id
            ? { ...item, cantidad: item.cantidad + 1 }
            : item
        );
      }

      return [
        ...current,
        {
          repuesto_id: producto.id,
          nombre: producto.nombre,
          codigo_referencia: producto.codigo_referencia,
          precio_unitario: number(producto.precio_venta),
          cantidad: 1,
          stock_actual: stock,
        },
      ];
    });
  };

  const updateQuantity = (repuestoId, value) => {
    setCart((current) =>
      current.map((item) => {
        if (item.repuesto_id !== repuestoId) return item;

        const parsed = Math.floor(Number(value));
        const quantity = Number.isFinite(parsed)
          ? Math.min(Math.max(parsed, 1), item.stock_actual)
          : 1;

        return { ...item, cantidad: quantity };
      })
    );
  };

  const removeFromCart = (repuestoId) => {
    setCart((current) =>
      current.filter((item) => item.repuesto_id !== repuestoId)
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (cart.length === 0) {
      setError("Agregue al menos un producto al carrito.");
      return;
    }

    setSaving(true);
    try {
      const data = await api.ventas.crear({
        usuario_id: user?.id || 1,
        notas: notas.trim(),
        items: cart.map((item) => ({
          repuesto_id: item.repuesto_id,
          cantidad: item.cantidad,
        })),
      });

      const venta = data.venta;
      setSuccess(venta);
      setCart([]);
      setNotas("");
      setProductos((current) =>
        current.map((producto) => {
          const detail = venta.detalles?.find(
            (detalle) => detalle.repuesto_id === producto.id
          );
          return detail
            ? { ...producto, stock_actual: detail.stock_nuevo }
            : producto;
        })
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  if (success) {
    return (
      <>
        <PageHeader
          eyebrow="Facturación"
          title="Venta registrada"
          description="La venta se procesó correctamente y el inventario fue actualizado."
          actions={
            <Link to="/ventas" className="btn btn-secondary">
              Volver al historial
            </Link>
          }
        />

        <section className="card success-card">
          <span className="success-icon">
            <Icon name="check" size={30} />
          </span>
          <span className="eyebrow">Factura generada</span>
          <h2>{success.numero_factura}</h2>
          <p className="muted">
            {success.items_vendidos} producto
            {success.items_vendidos === 1 ? "" : "s"} vendido
            {success.items_vendidos === 1 ? "" : "s"} · Total{" "}
            <strong>{money(success.total)}</strong>
          </p>

          <div className="success-actions">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setSuccess(null);
                setError("");
              }}
            >
              <Icon name="plus" size={17} />
              Registrar otra venta
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate("/ventas")}
            >
              Ver historial
              <Icon name="arrowRight" size={17} />
            </button>
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Facturación"
        title="Nueva venta"
        description="Seleccione los repuestos, ajuste las cantidades y confirme la factura."
        actions={
          <Link to="/ventas" className="btn btn-secondary">
            <Icon name="receipt" size={17} />
            Historial
          </Link>
        }
      />

      {error && (
        <Alert tone="danger" onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Spinner label="Cargando productos disponibles..." />
      ) : (
        <div className="sale-layout">
          <section className="card sale-catalog">
            <div className="card-header">
              <div>
                <h2>Productos disponibles</h2>
                <p>Haga clic en «Agregar» para incluirlo en la factura.</p>
              </div>
            </div>

            <div className="toolbar">
              <label className="search-field">
                <Icon name="search" size={18} />
                <input
                  type="search"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Buscar por nombre, referencia u OEM..."
                  aria-label="Buscar productos para la venta"
                />
              </label>

              <select
                className="select toolbar-select"
                value={catFilter}
                onChange={(event) => setCatFilter(event.target.value)}
                aria-label="Filtrar productos por categoría"
              >
                <option value="">Todas las categorías</option>
                {categorias.map((categoria) => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.nombre}
                  </option>
                ))}
              </select>
            </div>

            {filteredProducts.length === 0 ? (
              <EmptyState
                icon="box"
                title="No hay productos para esta búsqueda"
                description="Pruebe con otro término o cambie la categoría."
              />
            ) : (
              <div className="product-grid">
                {filteredProducts.map((producto) => {
                  const stock = number(producto.stock_actual);
                  const inCart = quantityInCart(producto.id);
                  const reachedLimit = stock <= 0 || inCart >= stock;

                  return (
                    <article className="product-card" key={producto.id}>
                      <div className="product-card-top">
                        <span
                          className="product-category"
                          title={producto.categoria_nombre || "General"}
                        >
                          {producto.categoria_nombre || "General"}
                        </span>
                        <span
                          className={`badge ${
                            stock <= 0
                              ? "badge-danger"
                              : stock <= number(producto.stock_minimo)
                                ? "badge-warning"
                                : "badge-success"
                          }`}
                        >
                          {stock <= 0
                            ? "Agotado"
                            : `${stock} ${stock === 1 ? "disponible" : "disponibles"}`}
                        </span>
                      </div>

                      <h3>{producto.nombre}</h3>
                      <p className="product-code">
                        {producto.codigo_referencia}
                        {producto.codigo_oem ? ` · OEM ${producto.codigo_oem}` : ""}
                      </p>

                      <div className="product-card-bottom">
                        <strong className="product-price">
                          {money(producto.precio_venta)}
                        </strong>
                        <button
                          type="button"
                          className="btn btn-primary btn-sm"
                          onClick={() => addToCart(producto)}
                          disabled={reachedLimit}
                        >
                          <Icon name="plus" size={15} />
                          {inCart > 0 ? `En carrito (${inCart})` : "Agregar"}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </section>

          <form className="card sale-cart" onSubmit={handleSubmit}>
            <div className="card-header">
              <div>
                <h2>Carrito</h2>
                <p>
                  {cartCount} unidad{cartCount === 1 ? "" : "es"} seleccionada
                  {cartCount === 1 ? "" : "s"}
                </p>
              </div>
              <span className="cart-count">
                <Icon name="cart" size={17} />
                {cart.length}
              </span>
            </div>

            {cart.length === 0 ? (
              <EmptyState
                icon="cart"
                title="El carrito está vacío"
                description="Agregue productos del catálogo para iniciar la venta."
              />
            ) : (
              <>
                <div className="cart-items">
                  {cart.map((item) => (
                    <div className="cart-item" key={item.repuesto_id}>
                      <div className="cart-item-info">
                        <strong>{item.nombre}</strong>
                        <small>
                          {item.codigo_referencia} · {money(item.precio_unitario)} c/u
                        </small>
                      </div>

                      <div className="quantity-control">
                        <button
                          type="button"
                          onClick={() =>
                            updateQuantity(item.repuesto_id, item.cantidad - 1)
                          }
                          disabled={item.cantidad <= 1}
                          aria-label={`Disminuir cantidad de ${item.nombre}`}
                        >
                          <Icon name="minus" size={14} />
                        </button>
                        <input
                          type="number"
                          min="1"
                          max={item.stock_actual}
                          value={item.cantidad}
                          onChange={(event) =>
                            updateQuantity(item.repuesto_id, event.target.value)
                          }
                          aria-label={`Cantidad de ${item.nombre}`}
                        />
                        <button
                          type="button"
                          onClick={() =>
                            updateQuantity(item.repuesto_id, item.cantidad + 1)
                          }
                          disabled={item.cantidad >= item.stock_actual}
                          aria-label={`Aumentar cantidad de ${item.nombre}`}
                        >
                          <Icon name="plus" size={14} />
                        </button>
                      </div>

                      <strong className="cart-item-subtotal">
                        {money(item.precio_unitario * item.cantidad)}
                      </strong>

                      <button
                        type="button"
                        className="icon-button danger"
                        onClick={() => removeFromCart(item.repuesto_id)}
                        aria-label={`Quitar ${item.nombre} del carrito`}
                      >
                        <Icon name="trash" size={16} />
                      </button>
                    </div>
                  ))}
                </div>

                <label className="field">
                  <span>Notas de la venta</span>
                  <textarea
                    rows="2"
                    value={notas}
                    onChange={(event) => setNotas(event.target.value)}
                    placeholder="Opcional: observaciones de la factura"
                  />
                </label>

                <div className="cart-totals">
                  <div>
                    <span>Subtotal</span>
                    <strong>{money(subtotal)}</strong>
                  </div>
                  <div>
                    <span>IVA</span>
                    <strong>{money(0)}</strong>
                  </div>
                  <div className="cart-total">
                    <span>Total</span>
                    <strong>{money(subtotal)}</strong>
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary btn-block"
                  disabled={saving}
                >
                  {saving ? "Procesando venta..." : "Confirmar venta"}
                  {!saving && <Icon name="arrowRight" size={17} />}
                </button>

                <p className="sale-seller">
                  Vendedor: <strong>{user?.nombre || "Usuario"}</strong>
                </p>
              </>
            )}
          </form>
        </div>
      )}
    </>
  );
}
