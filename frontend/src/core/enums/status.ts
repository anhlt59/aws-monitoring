/**
 * Agent deployment status
 * Maps to backend: src/domain/models/agent.py
 */
export enum AgentStatus {
  CreateComplete = 'CREATE_COMPLETE',
  CreateInProgress = 'CREATE_IN_PROGRESS',
  CreateFailed = 'CREATE_FAILED',
  UpdateComplete = 'UPDATE_COMPLETE',
  UpdateInProgress = 'UPDATE_IN_PROGRESS',
  UpdateFailed = 'UPDATE_FAILED',
  DeleteComplete = 'DELETE_COMPLETE',
  DeleteInProgress = 'DELETE_IN_PROGRESS',
  DeleteFailed = 'DELETE_FAILED',
  RollbackComplete = 'ROLLBACK_COMPLETE',
  RollbackInProgress = 'ROLLBACK_IN_PROGRESS'
}

/**
 * Agent status display configuration
 */
export const AGENT_STATUS_CONFIG = {
  [AgentStatus.CreateComplete]: {
    label: 'Active',
    color: 'green',
    icon: '🟢',
    className: 'text-green-600 bg-green-100'
  },
  [AgentStatus.CreateInProgress]: {
    label: 'Deploying',
    color: 'blue',
    icon: '🔵',
    className: 'text-blue-600 bg-blue-100'
  },
  [AgentStatus.CreateFailed]: {
    label: 'Failed',
    color: 'red',
    icon: '🔴',
    className: 'text-red-600 bg-red-100'
  },
  [AgentStatus.UpdateComplete]: {
    label: 'Active',
    color: 'green',
    icon: '🟢',
    className: 'text-green-600 bg-green-100'
  },
  [AgentStatus.UpdateInProgress]: {
    label: 'Updating',
    color: 'yellow',
    icon: '🟡',
    className: 'text-yellow-600 bg-yellow-100'
  },
  [AgentStatus.UpdateFailed]: {
    label: 'Failed',
    color: 'red',
    icon: '🔴',
    className: 'text-red-600 bg-red-100'
  },
  [AgentStatus.DeleteComplete]: {
    label: 'Deleted',
    color: 'gray',
    icon: '⚫',
    className: 'text-gray-600 bg-gray-100'
  },
  [AgentStatus.DeleteInProgress]: {
    label: 'Deleting',
    color: 'yellow',
    icon: '🟡',
    className: 'text-yellow-600 bg-yellow-100'
  },
  [AgentStatus.DeleteFailed]: {
    label: 'Delete Failed',
    color: 'red',
    icon: '🔴',
    className: 'text-red-600 bg-red-100'
  },
  [AgentStatus.RollbackComplete]: {
    label: 'Rolled Back',
    color: 'gray',
    icon: '⚫',
    className: 'text-gray-600 bg-gray-100'
  },
  [AgentStatus.RollbackInProgress]: {
    label: 'Rolling Back',
    color: 'yellow',
    icon: '🟡',
    className: 'text-yellow-600 bg-yellow-100'
  }
} as const;

/**
 * Helper function to check if agent is in a terminal state
 */
export function isTerminalStatus(status: AgentStatus): boolean {
  return [
    AgentStatus.CreateComplete,
    AgentStatus.CreateFailed,
    AgentStatus.UpdateComplete,
    AgentStatus.UpdateFailed,
    AgentStatus.DeleteComplete,
    AgentStatus.DeleteFailed,
    AgentStatus.RollbackComplete
  ].includes(status);
}

/**
 * Helper function to check if agent is active/healthy
 */
export function isActiveStatus(status: AgentStatus): boolean {
  return [
    AgentStatus.CreateComplete,
    AgentStatus.UpdateComplete
  ].includes(status);
}
