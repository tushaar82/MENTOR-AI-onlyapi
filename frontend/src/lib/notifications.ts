/**
 * Real-time Notification System
 *
 * This service handles real-time notifications for parents and students,
 * including AI insights, intervention alerts, and system notifications.
 * It uses polling for real-time updates and can be extended to use WebSocket.
 *
 * Author: Mentor AI Team
 * Version: 1.0.0
 */

import { aiFeaturesAPI } from './api';

// Types
interface NotificationData {
  id: string;
  type: 'insight' | 'alert' | 'system' | 'engagement' | 'performance';
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  data?: Record<string, any>;
  timestamp: string;
  read: boolean;
  action_required?: boolean;
  action_url?: string;
}

interface NotificationSettingsData {
  insights: boolean;
  alerts: boolean;
  system: boolean;
  engagement: boolean;
  performance: boolean;
  email: boolean;
  push: boolean;
  sound: boolean;
}

// Event types
type NotificationEvent =
  | 'notification_received'
  | 'notification_read'
  | 'notification_cleared'
  | 'connection_established'
  | 'connection_lost'
  | 'error';

// Event listener type
type NotificationEventListener = (data: any) => void;

// Export types
export type Notification = NotificationData;
export type NotificationSettings = NotificationSettingsData;
export type { NotificationEventListener };

class NotificationService {
  private notifications: Notification[] = [];
  private listeners: Map<NotificationEvent, NotificationEventListener[]> = new Map();
  private isPolling = false;
  private pollingInterval: NodeJS.Timeout | null = null;
  private userId: string | null = null;
  private settings: NotificationSettings = {
    insights: true,
    alerts: true,
    system: true,
    engagement: true,
    performance: true,
    email: true,
    push: true,
    sound: true,
  };

  /**
   * Initialize the notification service
   */
  async initialize(userId: string, settings?: Partial<NotificationSettings>): Promise<void> {
    this.userId = userId;
    if (settings) {
      this.settings = { ...this.settings, ...settings };
    }

    // Start polling for notifications
    this.startPolling();
  }


  /**
   * Start polling for notifications (fallback)
   */
  private startPolling(): void {
    if (this.isPolling) return;
    
    this.isPolling = true;
    console.log('Starting notification polling');
    
    this.pollingInterval = setInterval(async () => {
      try {
        await this.fetchNotifications();
      } catch (error) {
        console.error('Error polling notifications:', error);
      }
    }, 30000); // Poll every 30 seconds
  }

  /**
   * Stop polling
   */
  private stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    this.isPolling = false;
  }

  /**
   * Fetch notifications from API
   */
  private async fetchNotifications(): Promise<void> {
    if (!this.userId) return;

    try {
      const response = await aiFeaturesAPI.getCommunicationHistory({
        communication_type: 'notification',
        status: 'sent',
        limit: 50,
      });

      const newNotifications = response.data.map((comm: any) => ({
        id: comm.communication_id,
        type: comm.communication_type,
        title: comm.subject,
        message: comm.content,
        severity: comm.priority,
        data: comm.metadata,
        timestamp: comm.created_at,
        read: comm.status === 'read',
        action_required: comm.metadata?.action_required,
        action_url: comm.metadata?.action_url,
      }));

      // Find new notifications
      const existingIds = new Set(this.notifications.map(n => n.id));
      const newItems = newNotifications.filter((n: Notification) => !existingIds.has(n.id));

      if (newItems.length > 0) {
        this.notifications = [...newItems, ...this.notifications];
        newItems.forEach((notification: Notification) => {
          this.handleNewNotification(notification);
        });
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  }

  /**
   * Handle new notification
   */
  private handleNewNotification(notification: Notification): void {
    // Check if notification type is enabled in settings
    if (!this.settings[notification.type as keyof NotificationSettings]) {
      return;
    }

    // Add to notifications list
    this.notifications.unshift(notification);
    
    // Keep only last 100 notifications
    if (this.notifications.length > 100) {
      this.notifications = this.notifications.slice(0, 100);
    }

    // Emit event
    this.emit('notification_received', notification);

    // Show browser notification if enabled
    if (this.settings.push && 'Notification' in window && Notification.permission === 'granted') {
      this.showBrowserNotification(notification);
    }

    // Play sound if enabled
    if (this.settings.sound) {
      this.playNotificationSound(notification.severity);
    }
  }

  /**
   * Show browser notification
   */
  private showBrowserNotification(notification: Notification): void {
    const browserNotification = new Notification(notification.title, {
      body: notification.message,
      icon: '/favicon.ico',
      tag: notification.id,
      requireInteraction: notification.action_required,
    });

    browserNotification.onclick = () => {
      window.focus();
      if (notification.action_url) {
        window.location.href = notification.action_url;
      }
      browserNotification.close();
    };

    // Auto-close after 5 seconds if no action required
    if (!notification.action_required) {
      setTimeout(() => browserNotification.close(), 5000);
    }
  }

  /**
   * Play notification sound
   */
  private playNotificationSound(severity: string): void {
    try {
      const audio = new Audio();
      
      switch (severity) {
        case 'critical':
        case 'high':
          audio.src = '/sounds/alert-critical.mp3';
          break;
        case 'medium':
          audio.src = '/sounds/alert-medium.mp3';
          break;
        default:
          audio.src = '/sounds/notification.mp3';
      }
      
      audio.volume = 0.3;
      audio.play().catch(() => {
        // Ignore errors (user may not have interacted with page)
      });
    } catch (error) {
      // Ignore audio errors
    }
  }

  /**
   * Get all notifications
   */
  getNotifications(): Notification[] {
    return [...this.notifications];
  }

  /**
   * Get unread notifications
   */
  getUnreadNotifications(): Notification[] {
    return this.notifications.filter(n => !n.read);
  }

  /**
   * Get unread count
   */
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string): Promise<void> {
    const notification = this.notifications.find(n => n.id === notificationId);
    if (notification && !notification.read) {
      notification.read = true;
      
      // Update via API
      try {
        await aiFeaturesAPI.updateAlertStatus(notificationId, { status: 'acknowledged' });
      } catch (error) {
        console.error('Error marking notification as read:', error);
      }
      
      this.emit('notification_read', { notificationId });
    }
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    const unreadNotifications = this.notifications.filter(n => !n.read);
    
    for (const notification of unreadNotifications) {
      await this.markAsRead(notification.id);
    }
  }

  /**
   * Clear notification
   */
  clearNotification(notificationId: string): void {
    this.notifications = this.notifications.filter(n => n.id !== notificationId);
    this.emit('notification_cleared', { notificationId });
  }

  /**
   * Clear all notifications
   */
  clearAllNotifications(): void {
    this.notifications = [];
    this.emit('notification_cleared', { all: true });
  }

  /**
   * Update notification settings
   */
  updateSettings(newSettings: Partial<NotificationSettings>): void {
    this.settings = { ...this.settings, ...newSettings };
    
    // Save settings to backend
    this.saveSettings();
  }

  /**
   * Get current settings
   */
  getSettings(): NotificationSettings {
    return { ...this.settings };
  }

  /**
   * Save settings to backend
   */
  private async saveSettings(): Promise<void> {
    try {
      await aiFeaturesAPI.updateDashboardConfig({
        notification_preferences: {
          email: this.settings.email,
          push: this.settings.push,
          insights: this.settings.insights,
          alerts: this.settings.alerts,
          system: this.settings.system,
          engagement: this.settings.engagement,
          performance: this.settings.performance,
        },
      });
    } catch (error) {
      console.error('Error saving notification settings:', error);
    }
  }

  /**
   * Request browser notification permission
   */
  async requestNotificationPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  }

  /**
   * Add event listener
   */
  addEventListener(event: NotificationEvent, listener: NotificationEventListener): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }

  /**
   * Remove event listener
   */
  removeEventListener(event: NotificationEvent, listener: NotificationEventListener): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(listener);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  /**
   * Emit event
   */
  private emit(event: NotificationEvent, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error('Error in notification event listener:', error);
        }
      });
    }
  }

  /**
   * Disconnect from notification service
   */
  disconnect(): void {
    this.stopPolling();
    
    // Clear all listeners
    this.listeners.clear();
  }
}

// Create singleton instance
export const notificationService = new NotificationService();
