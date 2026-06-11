import { useAuth } from "../context/AuthContext";

export default function Topbar() {
  const { user, logout } = useAuth();

  return (
    <header className="h-14 border-b flex items-center justify-between px-4 bg-white">
      <div className="text-sm text-gray-600">
        Welcome, <span className="font-medium">{user?.name}</span>
      </div>

      <button
        onClick={logout}
        className="text-sm text-red-500 hover:text-red-700"
      >
        Logout
      </button>
    </header>
  );
}