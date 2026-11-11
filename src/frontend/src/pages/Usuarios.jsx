import { useEffect, useState } from "react";
import { api } from "../api";
import Alert from "../components/Alert";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icons";
import Modal from "../components/Modal";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";

const emptyForm = {
  nombre: "",
  email: "",
  password: "",
  rol_id: "",
  activo: true,
};

export default function Usuarios() {
  const { user } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [roles, setRoles] = useState([]);
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
    setLoading(true);
    setError("");

    api.usuarios
      .listar()
      .then((data) => {
        if (!active) return;
        setUsuarios(data.usuarios || []);
        setRoles(data.roles || []);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [refresh]);

  const openCreate = () => {
    setEditing(null);
    setForm({
      ...emptyForm,
      rol_id: roles[0]?.id ? String(roles[0].id) : "",
    });
    setFormError("");
    setModalOpen(true);
  };

  const openEdit = (usuario) => {
    setEditing(usuario);
    setForm({
      nombre: usuario.nombre || "",
      email: usuario.email || "",
      password: "",
      rol_id: String(usuario.rol_id),
      activo: Boolean(usuario.activo),
    });
    setFormError("");
    setModalOpen(true);
  };

  const updateField = (field) => (event) => {
    const value =
      event.target.type === "checkbox"
        ? event.target.checked
        : event.target.value;
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError("");

    if (!form.nombre.trim() || !form.email.trim() || !form.rol_id) {
      setFormError("Nombre, correo y rol son obligatorios.");
      return;
    }

    if (!editing && form.password.length < 8) {
      setFormError("La contraseña inicial debe tener al menos 8 caracteres.");
      return;
    }

    if (editing && form.password && form.password.length < 8) {
      setFormError("La nueva contraseña debe tener al menos 8 caracteres.");
      return;
    }

    const payload = {
      nombre: form.nombre.trim(),
      email: form.email.trim(),
      rol_id: Number(form.rol_id),
      activo: Boolean(form.activo),
    };
    if (form.password) {
      payload.password = form.password;
    }

    setSaving(true);
    try {
      if (editing) {
        await api.usuarios.actualizar(editing.id, payload);
        setNotice("Usuario actualizado correctamente.");
      } else {
        await api.usuarios.crear(payload);
        setNotice("Colaborador registrado correctamente.");
      }
      setModalOpen(false);
      setRefresh((value) => value + 1);
    } catch (requestError) {
      setFormError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSuspend = async (usuario) => {
    if (usuario.id === user?.id) {
      setError("No puede suspender su propia cuenta.");
      return;
    }
    const confirmed = window.confirm(
      `¿Suspender el acceso de "${usuario.nombre}"? Podrá reactivarlo después.`
    );
    if (!confirmed) return;

    try {
      await api.usuarios.desactivar(usuario.id);
      setNotice("Acceso suspendido correctamente.");
      setRefresh((value) => value + 1);
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const handleReactivate = async (usuario) => {
    try {
      await api.usuarios.actualizar(usuario.id, { activo: true });
      setNotice("Acceso reactivado correctamente.");
      setRefresh((value) => value + 1);
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Administración"
        title="Usuarios"
        description="Registre colaboradores, asigne su rol y controle el acceso al sistema."
        actions={
          <button type="button" className="btn btn-primary" onClick={openCreate}>
            <Icon name="plus" size={17} />
            Nuevo colaborador
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

      <section className="card">
        {loading ? (
          <Spinner label="Cargando usuarios..." />
        ) : usuarios.length === 0 ? (
          <EmptyState
            icon="users"
            title="No hay colaboradores registrados"
            description="Registre el primer usuario para asignarle un rol."
            action={
              <button type="button" className="btn btn-primary btn-sm" onClick={openCreate}>
                <Icon name="plus" size={16} />
                Nuevo colaborador
              </button>
            }
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Colaborador</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th className="actions-column">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((usuario) => (
                  <tr key={usuario.id}>
                    <td>
                      <strong>
                        {usuario.nombre}
                        {usuario.id === user?.id ? " (tú)" : ""}
                      </strong>
                      <small>{usuario.email}</small>
                    </td>
                    <td>
                      <span className="badge badge-info">{usuario.rol}</span>
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          usuario.activo ? "badge-success" : "badge-danger"
                        }`}
                      >
                        {usuario.activo ? "Activo" : "Suspendido"}
                      </span>
                    </td>
                    <td className="actions-column">
                      <div className="row-actions">
                        <button
                          type="button"
                          className="icon-button"
                          onClick={() => openEdit(usuario)}
                          title="Editar usuario"
                          aria-label={`Editar ${usuario.nombre}`}
                        >
                          <Icon name="edit" size={17} />
                        </button>
                        {usuario.activo ? (
                          <button
                            type="button"
                            className="icon-button danger"
                            onClick={() => handleSuspend(usuario)}
                            title="Suspender acceso"
                            aria-label={`Suspender ${usuario.nombre}`}
                            disabled={usuario.id === user?.id}
                          >
                            <Icon name="trash" size={17} />
                          </button>
                        ) : (
                          <button
                            type="button"
                            className="icon-button"
                            onClick={() => handleReactivate(usuario)}
                            title="Reactivar acceso"
                            aria-label={`Reactivar ${usuario.nombre}`}
                          >
                            <Icon name="refresh" size={17} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal
        open={modalOpen}
        title={editing ? "Editar colaborador" : "Nuevo colaborador"}
        subtitle={
          editing
            ? "Actualice los datos, el rol o el estado del acceso."
            : "Cree una cuenta y asígnele un rol de trabajo."
        }
        onClose={() => setModalOpen(false)}
      >
        {formError && <Alert tone="danger">{formError}</Alert>}

        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label className="field field-span-2">
              <span>Nombre completo *</span>
              <input
                value={form.nombre}
                onChange={updateField("nombre")}
                placeholder="Ej. Laura Gómez"
                required
              />
            </label>

            <label className="field field-span-2">
              <span>Correo electrónico *</span>
              <input
                type="email"
                value={form.email}
                onChange={updateField("email")}
                placeholder="colaborador@allquality.com"
                required
              />
            </label>

            <label className="field">
              <span>Rol *</span>
              <select
                value={form.rol_id}
                onChange={updateField("rol_id")}
                required
              >
                <option value="">Seleccione un rol</option>
                {roles.map((rol) => (
                  <option key={rol.id} value={rol.id}>
                    {rol.nombre}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>{editing ? "Nueva contraseña" : "Contraseña inicial *"}</span>
              <input
                type="password"
                value={form.password}
                onChange={updateField("password")}
                placeholder={editing ? "Dejar vacío para conservarla" : "Mínimo 8 caracteres"}
                autoComplete="new-password"
                required={!editing}
              />
              <small className="field-hint">
                Mínimo 8 caracteres. {editing ? "Déjela vacía para conservar la actual." : ""}
              </small>
            </label>

            {editing && (
              <label className="check-field field-span-2">
                <input
                  type="checkbox"
                  checked={form.activo}
                  onChange={updateField("activo")}
                />
                <span>
                  <strong>Acceso activo</strong>
                  <small>Desmarque para suspender el ingreso al sistema.</small>
                </span>
              </label>
            )}
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => setModalOpen(false)}
              disabled={saving}
            >
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Guardando..." : editing ? "Guardar cambios" : "Crear colaborador"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
