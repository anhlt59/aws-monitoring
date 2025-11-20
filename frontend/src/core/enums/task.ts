/**
 * Task status enum
 */
export enum TaskStatus {
  Open = 'open',
  InProgress = 'in_progress',
  Closed = 'closed'
}

export const TaskStatusLabels: Record<TaskStatus, string> = {
  [TaskStatus.Open]: 'Open',
  [TaskStatus.InProgress]: 'In Progress',
  [TaskStatus.Closed]: 'Closed'
}

export const TaskStatusColors: Record<TaskStatus, { bg: string; text: string }> = {
  [TaskStatus.Open]: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
  [TaskStatus.InProgress]: { bg: 'bg-blue-100', text: 'text-blue-800' },
  [TaskStatus.Closed]: { bg: 'bg-green-100', text: 'text-green-800' }
}

/**
 * Task priority enum
 */
export enum TaskPriority {
  Critical = 'critical',
  High = 'high',
  Medium = 'medium',
  Low = 'low'
}

export const TaskPriorityLabels: Record<TaskPriority, string> = {
  [TaskPriority.Critical]: 'Critical',
  [TaskPriority.High]: 'High',
  [TaskPriority.Medium]: 'Medium',
  [TaskPriority.Low]: 'Low'
}

export const TaskPriorityColors: Record<TaskPriority, { bg: string; text: string }> = {
  [TaskPriority.Critical]: { bg: 'bg-red-100', text: 'text-red-800' },
  [TaskPriority.High]: { bg: 'bg-orange-100', text: 'text-orange-800' },
  [TaskPriority.Medium]: { bg: 'bg-blue-100', text: 'text-blue-800' },
  [TaskPriority.Low]: { bg: 'bg-green-100', text: 'text-green-800' }
}
