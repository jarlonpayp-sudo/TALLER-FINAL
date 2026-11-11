const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

function buildQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      query.set(key, value);
    }
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

async function request(path, options = {}) {
  const token = localStorage.getItem("allquality_token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error(
      "No se pudo conectar con el servidor. Verifique que el backend esté en ejecución."
    );
  }

  const text = await response.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { error: text };
    }
  }

  if (!response.ok) {
    const error = new Error(data?.error || `Error HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }

  return data;
}

export const api = {
  health: () => request("/health"),

  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  productos: {
    listar: ({ q = "", cat = "" } = {}) =>
      request(`/productos${buildQuery({ q, cat })}`),
    obtener: (id) => request(`/productos/${id}`),
    crear: (data) =>
      request("/productos", { method: "POST", body: JSON.stringify(data) }),
    actualizar: (id, data) =>
      request(`/productos/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    desactivar: (id) => request(`/productos/${id}`, { method: "DELETE" }),
  },

  categorias: {
    listar: () => request("/categorias"),
  },

  inventario: {
    alertas: () => request("/inventario/alertas"),
    ajustar: (payload) =>
      request("/inventario/ajuste", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },

  ventas: {
    listar: (limit = 50) => request(`/ventas?limit=${limit}`),
    obtener: (id) => request(`/ventas/${id}`),
    crear: (payload) =>
      request("/ventas", { method: "POST", body: JSON.stringify(payload) }),
  },

  usuarios: {
    listar: () => request("/usuarios"),
    crear: (data) =>
      request("/usuarios", { method: "POST", body: JSON.stringify(data) }),
    actualizar: (id, data) =>
      request(`/usuarios/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    desactivar: (id) => request(`/usuarios/${id}`, { method: "DELETE" }),
  },
};
