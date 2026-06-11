import React, { useEffect, useState } from "react";
import {
  Users,
  Shield,
  ClipboardList,
  UserCheck,
  AlertCircle,
  Loader2,
} from "lucide-react";

import Card from "../../components/Card";
import { adminService } from "../../services/adminService";
import type { AdminStats, AdminUser } from "../../services/adminService";

/**
 * ----------------------------
 * ADMIN DASHBOARD
 * CLEAN + SCALABLE VERSION
 * ----------------------------
 */

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const load = async () => {
      try {
        const [statsData, usersData] = await Promise.all([
          adminService.getStats(),
          adminService.getAllUsers(),
        ]);

        setStats(statsData);
        setUsers(usersData);
      } catch (err) {
        setError("Failed to load admin dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  /**
   * ----------------------------
   * LOADING STATE
   * ----------------------------
   */
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    );
  }

  /**
   * ----------------------------
   * ERROR STATE
   * ----------------------------
   */
  if (error) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-2 rounded-lg">
          <AlertCircle size={18} />
          {error}
        </div>
      </div>
    );
  }

  /**
   * ----------------------------
   * DERIVED METRICS (PURE)
   * ----------------------------
   */
  const activeUsers = users.filter((u) => u.is_active).length;

  /**
   * ----------------------------
   * UI
   * ----------------------------
   */
  return (
    <div className="space-y-8">

      {/* HEADER */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Admin Control Panel
        </h1>
        <p className="text-sm text-gray-500">
          System governance and user management
        </p>
      </div>

      {/* STATS */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

          <Card className="flex items-center gap-4">
            <Users className="text-gray-600" />
            <div>
              <p className="text-sm text-gray-500">Total Users</p>
              <p className="text-xl font-bold">{stats.total_users}</p>
            </div>
          </Card>

          <Card className="flex items-center gap-4">
            <UserCheck className="text-green-600" />
            <div>
              <p className="text-sm text-gray-500">Active Users</p>
              <p className="text-xl font-bold">{activeUsers}</p>
            </div>
          </Card>

          <Card className="flex items-center gap-4">
            <Shield className="text-blue-600" />
            <div>
              <p className="text-sm text-gray-500">Admins</p>
              <p className="text-xl font-bold">{stats.total_admins}</p>
            </div>
          </Card>

          <Card className="flex items-center gap-4">
            <ClipboardList className="text-purple-600" />
            <div>
              <p className="text-sm text-gray-500">Assessments</p>
              <p className="text-xl font-bold">{stats.total_assessments}</p>
            </div>
          </Card>

        </div>
      )}

      {/* USERS TABLE */}
      <Card title="User Management">
        {users.length === 0 ? (
          <div className="py-10 text-center text-gray-500">
            No users found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-gray-500 border-b">
                <tr>
                  <th className="py-2">Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                </tr>
              </thead>

              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 font-medium">{u.name}</td>
                    <td>{u.email}</td>
                    <td className="capitalize">{u.role}</td>
                    <td>{u.is_active ? "Active" : "Inactive"}</td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}
      </Card>

    </div>
  );
};

export default AdminDashboard;