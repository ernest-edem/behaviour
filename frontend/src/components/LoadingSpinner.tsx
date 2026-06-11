import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center py-16 gap-3">
    <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
    <p className="text-sm text-gray-500">{message}</p>
  </div>
);

export default LoadingSpinner;
