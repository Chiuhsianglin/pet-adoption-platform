<template>
  <v-chip
    :color="statusColor"
    :variant="variant"
    :size="size"
  >
    {{ statusLabel }}
  </v-chip>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PetStatus } from '@/types/pet'

interface Props {
  status: PetStatus
  variant?: 'flat' | 'elevated' | 'tonal' | 'outlined' | 'text' | 'plain'
  size?: 'x-small' | 'small' | 'default' | 'large' | 'x-large'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'flat',
  size: 'default',
})

const statusColor = computed(() => {
  const colors: Record<PetStatus, string> = {
    [PetStatus.DRAFT]: 'grey',
    [PetStatus.PENDING_REVIEW]: 'warning',
    [PetStatus.AVAILABLE]: 'success',
    [PetStatus.PENDING]: 'info',
    [PetStatus.ADOPTED]: 'purple',
    [PetStatus.UNAVAILABLE]: 'error',
    [PetStatus.REJECTED]: 'red-darken-2',
  }
  return colors[props.status]
})

const statusLabel = computed(() => {
  const labels: Record<PetStatus, string> = {
    [PetStatus.DRAFT]: '草稿',
    [PetStatus.PENDING_REVIEW]: '審核中',
    [PetStatus.AVAILABLE]: '可領養',
    [PetStatus.PENDING]: '申請中',
    [PetStatus.ADOPTED]: '已領養',
    [PetStatus.UNAVAILABLE]: '暫停',
    [PetStatus.REJECTED]: '已拒絕',
  }
  return labels[props.status]
})
</script>
