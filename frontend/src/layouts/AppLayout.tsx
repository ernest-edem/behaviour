import React from "react";

interface Props {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<Props> = ({ children }) => {
  return (
    <div className="min-h-screen flex bg-gray-50">
      
      {/* SIDEBAR (placeholder if you have one) */}
      <aside className="w-64 bg-gray-900 text-white">
        Sidebar
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 p-6">
        {children}
      </main>

    </div>
  );
};

export default DashboardLayout;