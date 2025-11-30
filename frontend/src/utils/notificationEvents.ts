/**
 * Simple event bus for notification synchronization
 */
type NotificationEventCallback = () => void

class NotificationEventBus {
  private listeners: NotificationEventCallback[] = []

  on(callback: NotificationEventCallback) {
    this.listeners.push(callback)
  }

  off(callback: NotificationEventCallback) {
    this.listeners = this.listeners.filter(cb => cb !== callback)
  }

  emit() {
    this.listeners.forEach(callback => callback())
  }
}

export const notificationEvents = new NotificationEventBus()
