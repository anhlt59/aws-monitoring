/**
 * Event severity levels
 */
export enum Severity {
  Critical = 'critical',
  High = 'high',
  Medium = 'medium',
  Low = 'low',
  Unknown = 'unknown'
}

export const SeverityLabels: Record<Severity, string> = {
  [Severity.Critical]: 'Critical',
  [Severity.High]: 'High',
  [Severity.Medium]: 'Medium',
  [Severity.Low]: 'Low',
  [Severity.Unknown]: 'Unknown'
}

export const SeverityColors: Record<Severity, { bg: string; text: string; icon: string }> = {
  [Severity.Critical]: { bg: 'bg-red-100', text: 'text-red-800', icon: '🔴' },
  [Severity.High]: { bg: 'bg-orange-100', text: 'text-orange-800', icon: '🟠' },
  [Severity.Medium]: { bg: 'bg-blue-100', text: 'text-blue-800', icon: '🔵' },
  [Severity.Low]: { bg: 'bg-green-100', text: 'text-green-800', icon: '🟢' },
  [Severity.Unknown]: { bg: 'bg-gray-100', text: 'text-gray-800', icon: '⚪' }
}
