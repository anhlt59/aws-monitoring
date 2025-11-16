/**
 * Event severity levels
 * Maps to backend: src/domain/models/event.py
 */
export enum Severity {
  Unknown = 0,
  Low = 1,
  Medium = 2,
  High = 3,
  Critical = 4
}

/**
 * Severity display configuration
 */
export const SEVERITY_CONFIG = {
  [Severity.Critical]: {
    label: 'Critical',
    color: 'red',
    icon: '🔴',
    className: 'text-red-600 bg-red-100'
  },
  [Severity.High]: {
    label: 'High',
    color: 'orange',
    icon: '🟠',
    className: 'text-orange-600 bg-orange-100'
  },
  [Severity.Medium]: {
    label: 'Medium',
    color: 'blue',
    icon: '🔵',
    className: 'text-blue-600 bg-blue-100'
  },
  [Severity.Low]: {
    label: 'Low',
    color: 'green',
    icon: '🟢',
    className: 'text-green-600 bg-green-100'
  },
  [Severity.Unknown]: {
    label: 'Unknown',
    color: 'gray',
    icon: '⚪',
    className: 'text-gray-600 bg-gray-100'
  }
} as const;
