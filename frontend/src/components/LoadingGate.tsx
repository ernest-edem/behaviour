import React from "react";
import LoadingSpinner from "./LoadingSpinner";

interface Props {
  loading: boolean;
  children: React.ReactNode;
}

export default function LoadingGate({ loading, children }: Props) {
  if (loading) return <LoadingSpinner />;
  return <>{children}</>;
}