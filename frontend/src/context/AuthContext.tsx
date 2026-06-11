import React, { createContext, useContext, useEffect, useState } from "react";

export type UserRole = "user" | "clinician" | "admin";

export interface User {
  id?: string;
  name?: string;
  email?: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  role: UserRole | null;
  loading: boolean;

  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * ----------------------------
 * AUTH PROVIDER
 * ----------------------------
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [loading, setLoading] = useState(true);

  /**
   * ----------------------------
   * HYDRATE SESSION ON LOAD
   * ----------------------------
   */
  useEffect(() => {
    try {
      const storedToken = localStorage.getItem("token");
      const storedUser = localStorage.getItem("user");

      if (storedToken && storedUser) {
        const parsedUser: User = JSON.parse(storedUser);

        setToken(storedToken);
        setUser(parsedUser);
        setRole(parsedUser.role);
      }
    } catch (err) {
      console.error("Auth hydration failed:", err);
      localStorage.clear();
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * ----------------------------
   * LOGIN
   * ----------------------------
   */
  const login = (token: string, user: User) => {
    setToken(token);
    setUser(user);
    setRole(user.role);

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));

    setLoading(false);
  };

  /**
   * ----------------------------
   * LOGOUT
   * ----------------------------
   */
  const logout = () => {
    setToken(null);
    setUser(null);
    setRole(null);

    localStorage.removeItem("token");
    localStorage.removeItem("user");

    setLoading(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

/**
 * ----------------------------
 * HOOK
 * ----------------------------
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
};