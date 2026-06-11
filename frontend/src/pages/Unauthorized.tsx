import { useNavigate } from "react-router-dom";

export default function Unauthorized() {
  const navigate = useNavigate();

  return (
    <div className="h-screen flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold text-red-600">
        Unauthorized Access
      </h1>

      <p className="text-gray-600 mt-2">
        You do not have permission to view this page.
      </p>

      <button
        onClick={() => navigate("/")}
        className="mt-4 px-4 py-2 bg-black text-white rounded"
      >
        Go Home
      </button>
    </div>
  );
}