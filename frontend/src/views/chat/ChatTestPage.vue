<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="8" class="mx-auto">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chat-outline</v-icon>
            聊天功能測試頁面
          </v-card-title>
          
          <v-card-text>
            <v-alert type="info" class="mb-4">
              這是 Story 4.1 聊天功能的測試頁面
            </v-alert>

            <!-- Room Selection -->
            <v-select
              v-model="selectedRoomId"
              :items="rooms"
              item-title="name"
              item-value="id"
              label="選擇聊天室"
              :loading="loadingRooms"
              @update:model-value="onRoomChange"
            >
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props">
                  <template v-slot:append>
                    <v-chip 
                      v-if="item.raw.unread_count > 0" 
                      color="error" 
                      size="small"
                    >
                      {{ item.raw.unread_count }}
                    </v-chip>
                  </template>
                </v-list-item>
              </template>
            </v-select>

            <!-- Create New Room -->
            <v-btn 
              color="primary" 
              variant="outlined"
              @click="showCreateDialog = true"
              class="mb-4"
            >
              <v-icon class="mr-2">mdi-plus</v-icon>
              創建新聊天室
            </v-btn>

            <!-- Chat Box -->
            <ChatBox
              v-if="selectedRoomId"
              :room-id="selectedRoomId"
              :room-name="selectedRoomName"
            />
            
            <v-alert v-else type="warning">
              請選擇或創建一個聊天室
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create Room Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="500">
      <v-card>
        <v-card-title>創建新聊天室</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newRoomName"
            label="聊天室名稱"
            :rules="[v => !!v || '請輸入名稱']"
          />
          <v-text-field
            v-model="memberIdInput"
            label="成員 ID (用逗號分隔)"
            hint="例如: 1,2,3"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showCreateDialog = false">取消</v-btn>
          <v-btn 
            color="primary" 
            @click="createRoom"
            :loading="creating"
          >
            創建
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ChatBox from '@/components/chat/ChatBox.vue'
import { getUserChatRooms, createChatRoom } from '@/api/chat'
import type { ChatRoom } from '@/api/chat'

const rooms = ref<ChatRoom[]>([])
const selectedRoomId = ref<number>()
const selectedRoomName = ref<string>('')
const loadingRooms = ref(false)
const showCreateDialog = ref(false)
const newRoomName = ref('')
const memberIdInput = ref('')
const creating = ref(false)

const loadRooms = async () => {
  loadingRooms.value = true
  try {
    rooms.value = await getUserChatRooms()
    console.log('Loaded rooms:', rooms.value)
  } catch (error) {
    console.error('Failed to load rooms:', error)
  } finally {
    loadingRooms.value = false
  }
}

const onRoomChange = () => {
  const room = rooms.value.find(r => r.id === selectedRoomId.value)
  selectedRoomName.value = room?.name || ''
}

const createRoom = async () => {
  if (!newRoomName.value) return
  
  creating.value = true
  try {
    // Note: memberIds are handled by backend based on room type
    const room = await createChatRoom({
      name: newRoomName.value,
      type: 'GENERAL' // Default type for test
    })
    
    rooms.value.unshift(room)
    selectedRoomId.value = room.id
    selectedRoomName.value = room.name
    showCreateDialog.value = false
    newRoomName.value = ''
    memberIdInput.value = ''
  } catch (error) {
    console.error('Failed to create room:', error)
    alert('創建聊天室失敗')
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.v-container {
  padding-top: 20px;
}
</style>
