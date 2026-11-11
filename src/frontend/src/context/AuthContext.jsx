import { createContext, useContext, useMemo, useState } from "react";
import { api } from "../api";

const AuthContext = createContext(null);

function readUser() {
  try {
    const raw = localStorage.getItem("allquality_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readUser);
  const [token, setToken] = useState(() =>
    localStorage.getItem("allquality_token")
  );

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem("allquality_token", data.token);
    localStorage.setItem("allquality_user", JSON.stringify(data.usuario));
    setToken(data.token);
    setUser(data.usuario);
    return data;
  };

  const logout = () => {
    localStorage.removeItem("allquality_token");
    localStorage.removeItem("allquality_user");
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      logout,
      isAuthenticated: Boolean(token),
    }),
    [user, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return context;
}
