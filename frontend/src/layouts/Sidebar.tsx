import { NavLink } from "react-router-dom";
import { NAV_ITEMS } from "../config/navigation";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const { role } = useAuth();

  const items = NAV_ITEMS.filter((item) =>
    role ? item.roles.includes(role) : false
  );

  return (
    <aside className="w-64 h-screen bg-gray-900 text-white p-4">
      <h2 className="text-lg font-bold mb-6">Behaviour Lens AI</h2>

      <nav className="space-y-2">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block px-3 py-2 rounded-md text-sm transition ${
                isActive
                  ? "bg-gray-700"
                  : "hover:bg-gray-800"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}