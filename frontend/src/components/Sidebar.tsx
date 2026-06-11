import { NavLink } from "react-router-dom";
import type { UserRole } from "../auth/AuthContext";

interface Props {
  role: UserRole;
}

type MenuItem = {
  label: string;
  path: string;
  roles: UserRole[];
};

const MENU_ITEMS: MenuItem[] = [
  {
    label: "Dashboard",
    path: "/dashboard",
    roles: ["user", "clinician", "admin"],
  },
  {
    label: "Assessments",
    path: "/assessments",
    roles: ["user"],
  },
  {
    label: "Predictions",
    path: "/predictions",
    roles: ["user"],
  },
  {
    label: "Explanations",
    path: "/explanations",
    roles: ["user", "clinician", "admin"],
  },
  {
    label: "History",
    path: "/history",
    roles: ["user"],
  },
  {
    label: "Clinician Dashboard",
    path: "/clinician/dashboard",
    roles: ["clinician", "admin"],
  },
  {
    label: "Admin Dashboard",
    path: "/admin/dashboard",
    roles: ["admin"],
  },
];

export default function Sidebar({ role }: Props) {
  const visibleItems = MENU_ITEMS.filter((item) =>
    role ? item.roles.includes(role) : false
  );

  return (
    <aside className="w-64 bg-gray-900 text-white p-4 min-h-screen">
      <div className="text-xl font-bold mb-6">
        BehaviorLens AI
      </div>

      <nav className="space-y-2">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block px-3 py-2 rounded transition ${
                isActive ? "bg-gray-700" : "hover:bg-gray-800"
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