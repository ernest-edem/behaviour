import api from "../api/axios";

/**
 * -----------------------------
 * TYPES
 * -----------------------------
 */

export type UserRole = "user" | "clinician" | "admin";

export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_admins: number;
  total_assessments: number;
  active_users: number;
}

/**
 * Default fallback stats (safe UI rendering)
 */
const defaultStats: AdminStats = {
  total_users: 0,
  total_admins: 0,
  total_assessments: 0,
  active_users: 0,
};

/**
 * -----------------------------
 * ADMIN SERVICE
 * -----------------------------
 */

export const adminService = {
  /**
   * Get all users in system
   */
  async getAllUsers(): Promise<AdminUser[]> {
    try {
      const res = await api.get("/admin/users");

      // defensive extraction (handles both {data: []} and direct [])
      return Array.isArray(res.data)
        ? res.data
        : res.data?.data ?? [];
    } catch (error) {
      console.error("adminService.getAllUsers failed:", error);
      return [];
    }
  },

  /**
   * Get system-wide admin stats
   */
  async getStats(): Promise<AdminStats> {
    try {
      const res = await api.get("/admin/stats");

      // backend might return:
      // 1. raw object
      // 2. { data: object }
      return {
        ...defaultStats,
        ...(res.data?.data ?? res.data),
      };
    } catch (error) {
      console.error("adminService.getStats failed:", error);
      return defaultStats;
    }
  },
};