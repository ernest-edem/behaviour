import React from 'react';
import type { RiskLevel } from '../types';
import { formatRiskLevel, getRiskBadgeClasses } from '../utils/risk';

interface RiskBadgeProps {
  level: RiskLevel;
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ level }) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getRiskBadgeClasses(level)}`}
  >
    {formatRiskLevel(level)}
  </span>
);

export default RiskBadge;
