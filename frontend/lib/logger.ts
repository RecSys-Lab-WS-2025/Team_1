/**
 * Unified logging utility module.
 * 
 * Provides a structured logging system for the frontend application with:
 * - Multiple log levels (DEBUG, INFO, WARN, ERROR)
 * - Automatic dev/production behavior switching
 * - Log grouping and formatting
 * - Performance monitoring
 * - Request tracing
 * - localStorage persistence (ERROR and WARN)
 * - Automatic sending to backend (ERROR and WARN)
 * 
 * Usage:
 *   import { logger } from '@/lib/logger';
 *   
 *   logger.debug('Debug information');
 *   logger.info('General information');
 *   logger.warn('Warning information');
 *   logger.error('Error information', error);
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: unknown;
  component?: string;
  action?: string;
  userAgent?: string;
  url?: string;
  stack?: string;
}

class Logger {
  private isDevelopment: boolean;
  private logHistory: LogEntry[] = [];
  private maxHistorySize: number = 100;
  private localStorageKey = 'trailsaga-frontend-logs';
  private maxLocalStorageSize: number = 500; // Maximum 500 error/warn logs in localStorage
  private pendingLogs: LogEntry[] = []; // Logs waiting to be sent to backend
  private sendLogsInterval: number = 30000; // Send every 30 seconds
  private sendLogsTimer: NodeJS.Timeout | null = null;
  private apiBaseUrl: string;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    this.loadFromLocalStorage();
    this.startAutoSend();
    
    // On page unload, try to send any pending logs
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.flushPendingLogs();
      });
    }
  }

  /**
   * Format log message
   */
  private formatMessage(
    level: LogLevel,
    message: string,
    component?: string,
    action?: string
  ): string {
    const timestamp = new Date().toISOString();
    const prefix = component ? `[${component}]` : '';
    const actionPrefix = action ? `[${action}]` : '';
    const emoji = this.getEmoji(level);
    
    return `${emoji} ${timestamp} ${prefix} ${actionPrefix} ${message}`;
  }

  /**
   * Get emoji for log level
   */
  private getEmoji(level: LogLevel): string {
    switch (level) {
      case 'debug':
        return '🔍';
      case 'info':
        return 'ℹ️';
      case 'warn':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return '📝';
    }
  }

  /**
   * Add log entry to in-memory history
   */
  private addToHistory(entry: LogEntry): void {
    this.logHistory.push(entry);
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift();
    }

    // For ERROR and WARN, persist to localStorage and queue for backend sending
    if (entry.level === 'error' || entry.level === 'warn') {
      this.persistToLocalStorage(entry);
      this.addToPendingLogs(entry);
    }
  }

  /**
   * Persist a log entry to localStorage
   */
  private persistToLocalStorage(entry: LogEntry): void {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(this.localStorageKey);
      let logs: LogEntry[] = stored ? JSON.parse(stored) : [];
      
      // Enrich with user agent and URL information
      const enrichedEntry: LogEntry = {
        ...entry,
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
        url: typeof window !== 'undefined' ? window.location.href : undefined,
        stack: entry.data instanceof Error ? entry.data.stack : undefined,
      };
      
      logs.push(enrichedEntry);
      
      // Limit the number of stored logs
      if (logs.length > this.maxLocalStorageSize) {
        logs = logs.slice(-this.maxLocalStorageSize);
      }
      
      localStorage.setItem(this.localStorageKey, JSON.stringify(logs));
    } catch (error) {
      // localStorage may be full or unavailable; fail silently
      console.warn('Failed to persist log to localStorage:', error);
    }
  }

  /**
   * Load logs from localStorage into memory
   */
  private loadFromLocalStorage(): void {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(this.localStorageKey);
      if (stored) {
        const logs: LogEntry[] = JSON.parse(stored);
        // Only keep the most recent logs in memory
        this.logHistory = logs.slice(-this.maxHistorySize);
      }
    } catch (error) {
      console.warn('Failed to load logs from localStorage:', error);
    }
  }

  /**
   * Add entry to pending-send queue
   */
  private addToPendingLogs(entry: LogEntry): void {
    this.pendingLogs.push(entry);
    
    // If too many pending logs, flush immediately
    if (this.pendingLogs.length >= 10) {
      this.flushPendingLogs();
    }
  }
  
  /**
   * Start periodic auto-send timer
   */
  private startAutoSend(): void {
    if (typeof window === 'undefined') return;
    
    this.sendLogsTimer = setInterval(() => {
      this.flushPendingLogs();
    }, this.sendLogsInterval);
  }

  /**
   * Send pending logs to backend
   */
  private async flushPendingLogs(): Promise<void> {
    if (this.pendingLogs.length === 0) return;

    const logsToSend = [...this.pendingLogs];
    this.pendingLogs = [];

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/logs/frontend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          logs: logsToSend,
          timestamp: new Date().toISOString(),
        }),
      });
  
      if (!response.ok) {
        // If sending fails, re-queue logs (with size limit)
        this.pendingLogs = [...logsToSend, ...this.pendingLogs].slice(0, 100);
      }
    } catch (error) {
      // Network error: re-queue logs (with size limit)
      this.pendingLogs = [...logsToSend, ...this.pendingLogs].slice(0, 100);
    }
  }
  
  /**
   * Core log output method
   */
  private log(
    level: LogLevel,
    message: string,
    data?: unknown,
    component?: string,
    action?: string
  ): void {
    const formattedMessage = this.formatMessage(level, message, component, action);
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      data,
      component,
      action,
    };

    this.addToHistory(entry);
    
    // In production, only output ERROR and WARN to console
    if (!this.isDevelopment && level !== 'error' && level !== 'warn') {
      return;
    }
    
    // Use console methods for actual output
    switch (level) {
      case 'debug':
        if (this.isDevelopment) {
          console.debug(formattedMessage, data || '');
        }
        break;
      case 'info':
        console.info(formattedMessage, data || '');
        break;
      case 'warn':
        console.warn(formattedMessage, data || '');
        break;
      case 'error':
        console.error(formattedMessage, data || '');
        break;
    }
  }

  /**
   * Debug log
   */
  debug(message: string, data?: unknown, component?: string, action?: string): void {
    this.log('debug', message, data, component, action);
  }

  /**
   * Info log
   */
  info(message: string, data?: unknown, component?: string, action?: string): void {
    this.log('info', message, data, component, action);
  }

  /**
   * Warning log
   */
  warn(message: string, data?: unknown, component?: string, action?: string): void {
    this.log('warn', message, data, component, action);
  }

  /**
   * Error log
   */
  error(message: string, error?: unknown, component?: string, action?: string): void {
    this.log('error', message, error, component, action);
  }

  /**
   * Log API request
   */
  logApiRequest(
    method: string,
    url: string,
    data?: unknown,
    component?: string
  ): void {
    this.info(
      `API request: ${method} ${url}`,
      data,
      component,
      'API_REQUEST'
    );
  }

  /**
   * Log API response
   */
  logApiResponse(
    method: string,
    url: string,
    status: number,
    duration: number,
    data?: unknown,
    component?: string
  ): void {
    const statusEmoji = status >= 200 && status < 300 ? '✅' : '❌';
    this.info(
      `${statusEmoji} API response: ${method} ${url} | status=${status} | duration=${duration.toFixed(2)}ms`,
      data,
      component,
      'API_RESPONSE'
    );
  }
  
  /**
   * Log API error
   */
  logApiError(
    method: string,
    url: string,
    error: unknown,
    component?: string
  ): void {
    this.error(
      `API error: ${method} ${url}`,
      error,
      component,
      'API_ERROR'
    );
  }

  /**
   * Log component lifecycle
   */
  logComponentLifecycle(
    component: string,
    lifecycle: 'mount' | 'unmount' | 'update',
    props?: unknown
  ): void {
    const action = lifecycle === 'mount' ? 'MOUNT' : 
                   lifecycle === 'unmount' ? 'UNMOUNT' : 'UPDATE';
    this.debug(
      `Component ${lifecycle}: ${component}`,
      props,
      component,
      action
    );
  }
  
  /**
   * Log business logic operations
   */
  logBusinessLogic(
    action: string,
    entity: string,
    entityId?: number | string,
    data?: unknown,
    component?: string
  ): void {
    const message = entityId 
      ? `${action} ${entity} (id=${entityId})`
      : `${action} ${entity}`;
    this.info(message, data, component, 'BUSINESS_LOGIC');
  }
  
  /**
   * Log performance metrics
   */
  logPerformance(
    operation: string,
    duration: number,
    component?: string,
    metadata?: unknown
  ): void {
    const emoji = duration > 1000 ? '🐌' : duration > 500 ? '⏱️' : '⚡';
    this.debug(
      `${emoji} Performance: ${operation} | duration=${duration.toFixed(2)}ms`,
      metadata,
      component,
      'PERFORMANCE'
    );
  }
  
  /**
   * Log user actions
   */
  logUserAction(
    action: string,
    data?: unknown,
    component?: string
  ): void {
    this.info(
      `👤 User action: ${action}`,
      data,
      component,
      'USER_ACTION'
    );
  }
  
  /**
   * Group logs (for complex operations)
   */
  group(label: string, component?: string): void {
    if (this.isDevelopment) {
      console.group(`📦 ${label}${component ? ` [${component}]` : ''}`);
    }
  }

  groupEnd(): void {
    if (this.isDevelopment) {
      console.groupEnd();
    }
  }

  /**
   * Get log history
   */
  getHistory(level?: LogLevel, limit?: number): LogEntry[] {
    let filtered = this.logHistory;
    
    if (level) {
      filtered = filtered.filter(entry => entry.level === level);
    }
    
    if (limit) {
      filtered = filtered.slice(-limit);
    }
    
    return filtered;
  }

  /**
   * Clear in-memory log history
   */
  clearHistory(): void {
    this.logHistory = [];
  }

  /**
   * Export log history as JSON (for debugging)
   */
  exportHistory(): string {
    return JSON.stringify(this.logHistory, null, 2);
  }

  /**
   * Get all persisted logs from localStorage
   */
  getPersistedLogs(level?: LogLevel): LogEntry[] {
    if (typeof window === 'undefined') return [];

    try {
      const stored = localStorage.getItem(this.localStorageKey);
      if (!stored) return [];

      const logs: LogEntry[] = JSON.parse(stored);
      if (level) {
        return logs.filter(log => log.level === level);
      }
      return logs;
    } catch (error) {
      console.warn('Failed to get persisted logs:', error);
      return [];
    }
  }

  /**
   * Clear logs stored in localStorage
   */
  clearPersistedLogs(): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.removeItem(this.localStorageKey);
    } catch (error) {
      console.warn('Failed to clear persisted logs:', error);
    }
  }

  /**
   * Export persisted logs as JSON string
   */
  exportPersistedLogs(level?: LogLevel): string {
    const logs = this.getPersistedLogs(level);
    return JSON.stringify(logs, null, 2);
  }

  /**
   * Export persisted logs as a downloadable file
   */
  downloadPersistedLogs(level?: LogLevel): void {
    if (typeof window === 'undefined') return;

    const logs = this.getPersistedLogs(level);
    const json = JSON.stringify(logs, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frontend-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Manually send pending logs to backend
   */
  async sendLogsToBackend(): Promise<boolean> {
    await this.flushPendingLogs();
    return this.pendingLogs.length === 0;
  }
}

// Export singleton
export const logger = new Logger();

// Export types
export type { LogLevel, LogEntry };

