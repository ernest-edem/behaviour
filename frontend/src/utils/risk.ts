import type { RiskLevel } from '../types';

export function getRiskBadgeClasses(level: RiskLevel): string {
  switch (level) {
    case 'low':
    case 'mild':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'moderate':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'high':
    case 'critical':
      return 'bg-red-100 text-red-800 border-red-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

export function getRiskCardBorder(level: RiskLevel): string {
  switch (level) {
    case 'low':
    case 'mild':
      return 'border-l-green-500';
    case 'moderate':
      return 'border-l-yellow-500';
    case 'high':
    case 'critical':
      return 'border-l-red-500';
    default:
      return 'border-l-gray-300';
  }
}

export function formatRiskLevel(level: RiskLevel): string {
  return level.charAt(0).toUpperCase() + level.slice(1);
}

export function formatCondition(condition: string): string {
  return condition
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function confidenceToPercent(score: number): number {
  return Math.round(score * 100);
}

export function getSeverityColor(contribution: number): string {
  if (contribution >= 0.3) return 'bg-red-500';
  if (contribution >= 0.15) return 'bg-yellow-500';
  return 'bg-green-500';
}
