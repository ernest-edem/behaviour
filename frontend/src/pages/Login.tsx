import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { authService } from "../services/authService";
import {
  Activity,
  Lock,
  Mail,
  AlertCircle,
  Loader2,
} from "lucide-react";
/*import { getApiErrorMessage } from "../utils/format";*/

import { DEFAULT_ROUTES } from "../utils/rbacRoutes";

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await authService.login({
        email,
        password,
      });

      // AuthContext expects (token, role)
      login(data.access_token, data.role);

      const from = location.state?.from?.pathname || DEFAULT_ROUTES[data.role];
      navigate(from, { replace: true });
    } catch (err: any) {
      console.log("LOGIN ERROR:", err);
      
      console.log("response =", err?.response);

      console.log("status =", err?.response?.status);

      console.log("data =", err?.response?.data);
      setError(
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Failed to login."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl">
        <div className="text-center">
          <Activity className="mx-auto h-12 w-12 text-primary-600" />

          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Welcome back
          </h2>

          <p className="mt-2 text-sm text-gray-600">
            Sign in to your BehaviorLens AI account
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg flex items-center gap-2 text-sm">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div className="rounded-md shadow-sm space-y-4">
            <div className="relative">
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Email Address
              </label>

              <div className="absolute inset-y-0 left-0 pl-3 pt-6 flex items-center pointer-events-none text-gray-400">
                <Mail size={18} />
              </div>

              <input
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 sm:text-sm"
              />
            </div>

            <div className="relative">
              <label className="text-sm font-medium text-gray-700 mb-1 block">
                Password
              </label>

              <div className="absolute inset-y-0 left-0 pl-3 pt-6 flex items-center pointer-events-none text-gray-400">
                <Lock size={18} />
              </div>

              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-semibold rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 transition-all"
            >
              {loading ? (
                <Loader2 className="animate-spin h-5 w-5" />
              ) : (
                "Sign in"
              )}
            </button>
          </div>
        </form>

        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;