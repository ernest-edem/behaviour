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
  role?: string; // IMPORTANT: backend may send inconsistent format
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

/**
 * Normalize ANY backend role format into strict frontend role
 */
function normalizeRole(role: string | null | undefined): UserRole | null {
  if (!role) return null;

  const r = role.toLowerCase().trim();

  // handle common backend formats
  if (r === "admin" || r === "role_admin" || r === "administrator") return "admin";
  if (r === "clinician" || r === "role_clinician") return "clinician";
  if (r === "user" || r === "role_user") return "user";

  return null;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [loading, setLoading] = useState(true);

  /**
   * Bootstrap auth state safely from localStorage + JWT
   */
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedRole = localStorage.getItem(ROLE_KEY);

    if (!storedToken) {
      setToken(null);
      setRole(null);
      setLoading(false);
      return;
    }

    try {
      const decoded = jwtDecode<DecodedToken>(storedToken);

      const decodedRole = normalizeRole(decoded.role);
      const storedRoleNormalized = normalizeRole(storedRole as string);

      const finalRole = decodedRole || storedRoleNormalized;

      setToken(storedToken);
      setRole(finalRole);
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

  /**
   * LOGIN
   */
  const login = (newToken: string, newRole: UserRole) => {
    const normalizedRole = normalizeRole(newRole);

    if (!normalizedRole) {
      console.error("Invalid role provided to login:", newRole);
      return;
    }

    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(ROLE_KEY, normalizedRole);

    setToken(newToken);
    setRole(normalizedRole);
  };

  /**
   * LOGOUT
   */
  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);

    setToken(null);
    setRole(null);
  };

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

/**
 * Hook
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
};