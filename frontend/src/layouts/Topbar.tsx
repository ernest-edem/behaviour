import { useAuth } from "../auth/AuthContext";

export default function Topbar() {
  const { role, logout } = useAuth();

  return (
    <header className="h-14 border-b flex items-center justify-between px-4 bg-white">
      <div className="text-sm text-gray-600">
        Logged in as{" "}
        <span className="font-medium capitalize">
          {role}
        </span>
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