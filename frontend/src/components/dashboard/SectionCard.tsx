import React from "react";

interface Props {
  title: string;
  children: React.ReactNode;
}

export default function SectionCard({ title, children }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        {title}
      </h3>
      {children}
    </div>
  );
}