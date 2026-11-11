import Icon from "./Icons";

export default function Alert({ tone = "info", children, onClose }) {
  return (
    <div className={`alert alert-${tone}`} role="status">
      <span>{children}</span>
      {onClose && (
        <button
          type="button"
          className="alert-close"
          onClick={onClose}
          aria-label="Cerrar mensaje"
        >
          <Icon name="close" size={15} />
        </button>
      )}
    </div>
  );
}
