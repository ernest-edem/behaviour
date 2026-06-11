import { apiClient } from "./client";


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
 * -----------------------------
 * SERVICE LAYER (ADMIN API)
 * -----------------------------
 */

export const adminService = {
  /**
   * Get all users in system
   */
  async getAllUsers(): Promise<AdminUser[]> {
    try {
      const res = await apiClient.get("/admin/users");
      return res.data ?? [];
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
      const res = await apiClient.get("/admin/stats");
      return (
        res.data ?? {
          total_users: 0,
          total_admins: 0,
          total_assessments: 0,
          active_users: 0,
        }
      );
    } catch (error) {
      console.error("adminService.getStats failed:", error);

      return {
        total_users: 0,
        total_admins: 0,
        total_assessments: 0,
        active_users: 0,
      };
    }
  },
};