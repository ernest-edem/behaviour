export type Role = "user" | "admin" | "clinician";

export interface NavItem {
  label: string;
  path: string;
  roles: Role[];
}

export const NAV_ITEMS: NavItem[] = [
  {
    label: "Dashboard",
    path: "/user",
    roles: ["user"],
  },
  {
    label: "My Assessments",
    path: "/user/assessments",
    roles: ["user"],
  },

  {
    label: "Clinician Panel",
    path: "/clinician",
    roles: ["clinician"],
  },
  {
    label: "Patients",
    path: "/clinician/patients",
    roles: ["clinician"],
  },

  {
    label: "Admin Dashboard",
    path: "/admin",
    roles: ["admin"],
  },
  {
    label: "User Management",
    path: "/admin/users",
    roles: ["admin"],
  },
];