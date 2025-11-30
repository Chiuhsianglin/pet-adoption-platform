/**
 * Chat WebSocket Service
 * 管理聊天室的 WebSocket 連接、訂閱和訊息監聽
 */

import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

export interface WebSocketMessage {
  type: 'subscribed' | 'unsubscribed' | 'new_message' | 'pong' | 'error';
  room_id?: number;
  message?: any;
  error?: string;
}

export interface MessageListener {
  (message: WebSocketMessage): void;
}

class ChatWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimeout: number | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private listeners: Set<MessageListener> = new Set();
  private subscribedRooms: Set<number> = new Set();
  private heartbeatInterval: number | null = null;
  
  public connected = ref(false);
  public connecting = ref(false);

  /**
   * 連接 WebSocket
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('✅ WebSocket already connected');
      return;
    }

    if (this.connecting.value) {
      console.log('⏳ WebSocket connection in progress...');
      return;
    }

    try {
      this.connecting.value = true;
      const authStore = useAuthStore();
      const token = authStore.token;

      if (!token) {
        throw new Error('No authentication token available');
      }

      // 使用 V2 API 端點
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = import.meta.env.VITE_API_BASE_URL?.replace(/^https?:\/\//, '') || 'localhost:8000';
      const wsUrl = `${protocol}//${host}/api/v2/chat/ws?token=${token}`;

      console.log('🔌 Connecting to WebSocket V2:', wsUrl);

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.connected.value = true;
        this.connecting.value = false;
        this.reconnectAttempts = 0;

        // 重新訂閱之前的聊天室
        this.subscribedRooms.forEach(roomId => {
          this.subscribeRoom(roomId);
        });

        // 啟動心跳檢測
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', message);

          // 通知所有監聽器
          this.listeners.forEach(listener => {
            listener(message);
          });
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.connecting.value = false;
      };

      this.ws.onclose = (event) => {
        console.log('❌ WebSocket closed:', event.code, event.reason);
        this.connected.value = false;
        this.connecting.value = false;
        this.stopHeartbeat();

        // 自動重連
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          
          this.reconnectTimeout = window.setTimeout(() => {
            this.connect();
          }, this.reconnectDelay);
        } else {
          console.error('❌ Max reconnection attempts reached');
        }
      };

    } catch (error) {
      console.error('❌ Failed to connect WebSocket:', error);
      this.connecting.value = false;
      throw error;
    }
  }

  /**
   * 斷開 WebSocket 連接
   */
  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket...');
    
    // 清除重連定時器
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    // 停止心跳
    this.stopHeartbeat();

    // 關閉連接
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.connected.value = false;
    this.connecting.value = false;
    this.subscribedRooms.clear();
  }

  /**
   * 訂閱聊天室
   */
  subscribeRoom(roomId: number): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not connected, cannot subscribe to room');
      this.subscribedRooms.add(roomId); // 記住，連接後重新訂閱
      return;
    }

    console.log('📢 Subscribing to room:', roomId);
    this.subscribedRooms.add(roomId);

    this.ws.send(JSON.stringify({
      action: 'subscribe',
      room_id: roomId
    }));
  }

  /**
   * 取消訂閱聊天室
   */
  unsubscribeRoom(roomId: number): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not connected, cannot unsubscribe from room');
      return;
    }

    console.log('🔕 Unsubscribing from room:', roomId);
    this.subscribedRooms.delete(roomId);

    this.ws.send(JSON.stringify({
      action: 'unsubscribe',
      room_id: roomId
    }));
  }

  /**
   * 添加訊息監聽器
   */
  addListener(listener: MessageListener): void {
    this.listeners.add(listener);
  }

  /**
   * 移除訊息監聽器
   */
  removeListener(listener: MessageListener): void {
    this.listeners.delete(listener);
  }

  /**
   * 啟動心跳檢測
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();

    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000); // 每 30 秒發送一次心跳
  }

  /**
   * 停止心跳檢測
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * 獲取連接狀態
   */
  get isConnected(): boolean {
    return this.connected.value;
  }

  /**
   * 獲取連接中狀態
   */
  get isConnecting(): boolean {
    return this.connecting.value;
  }
}

// 創建單例
export const chatWebSocket = new ChatWebSocketService();
