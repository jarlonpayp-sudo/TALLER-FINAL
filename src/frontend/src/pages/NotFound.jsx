import { Link } from "react-router-dom";
import Icon from "../components/Icons";

export default function NotFound() {
  return (
    <main className="not-found">
      <span className="not-found-code">404</span>
      <h1>Página no encontrada</h1>
      <p>La dirección que intentó abrir no existe en AllQuality.</p>
      <Link to="/" className="btn btn-primary">
        <Icon name="grid" size={17} />
        Volver al panel
      </Link>
    </main>
  );
}
