import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { jwtDecode } from "jwt-decode";

export type UserRole = "admin" | "clinician" | "user";

interface DecodedToken {
  sub: string | number;
  role: UserRole;
  exp?: number;
}

interface AuthContextType {
  token: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  loading: boolean;
  login: (token: string, role: UserRole) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "token";
const ROLE_KEY = "role";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  

  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [loading, setLoading] = useState(true);

  // -----------------------------
  // BOOTSTRAP AUTH STATE
  // -----------------------------
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedRole = localStorage.getItem(ROLE_KEY) as UserRole | null;

      if (storedToken) {
        const decoded = jwtDecode<DecodedToken>(storedToken);

        setToken(storedToken);

        // Prefer decoded role (source of truth)
        setRole(decoded.role || storedRole);
      } else {
        setToken(null);
        setRole(null);
      }
    } catch (err) {
      console.error("Auth bootstrap failed:", err);
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(ROLE_KEY);
      setToken(null);
      setRole(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // -----------------------------
  // LOGIN
  // -----------------------------
  const login = (newToken: string, newRole: UserRole) => {
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(ROLE_KEY, newRole);
  
    setToken(newToken);
    setRole(newRole);
  };

  // -----------------------------
  // LOGOUT
  // -----------------------------
  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
  
    setToken(null);
    setRole(null);
  };

  // -----------------------------
  // DERIVED STATE (MEMOIZED)
  // -----------------------------
  const value = useMemo<AuthContextType>(
    () => ({
      token,
      role,
      isAuthenticated: !!token,
      isAdmin: role === "admin",
      loading,
      login,
      logout,
    }),
    [token, role, loading]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
};