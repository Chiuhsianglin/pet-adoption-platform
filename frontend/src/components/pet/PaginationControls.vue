<template>
  <div class="pagination-controls">
    <v-row align="center" justify="center" no-gutters>
      <!-- Results Info -->
      <v-col cols="12" md="auto" class="text-center text-md-left mb-3 mb-md-0">
        <div class="text-body-2 text-medium-emphasis">
          顯示 <strong>{{ startItem }}-{{ endItem }}</strong> / 共 <strong>{{ total }}</strong> 筆
        </div>
      </v-col>

      <v-spacer class="d-none d-md-block" />

      <!-- Pagination -->
      <v-col cols="12" md="auto" class="d-flex justify-center">
        <v-pagination
          :model-value="page"
          :length="totalPages"
          :total-visible="7"
          @update:model-value="handlePageChange"
        />
      </v-col>

      <v-spacer class="d-none d-md-block" />

      <!-- Page Size Selector -->
      <v-col cols="12" md="auto" class="d-flex justify-center justify-md-end mt-3 mt-md-0">
        <div class="d-flex align-center">
          <span class="text-body-2 text-medium-emphasis mr-2">每頁顯示：</span>
          <v-select
            :model-value="pageSize"
            :items="pageSizeOptions"
            density="compact"
            variant="outlined"
            hide-details
            class="page-size-select"
            @update:model-value="handlePageSizeChange"
          />
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  page: number
  pageSize: number
  total: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:page': [value: number]
  'update:page-size': [value: number]
}>()

const pageSizeOptions = [
  { title: '12', value: 12 },
  { title: '24', value: 24 },
  { title: '48', value: 48 },
  { title: '96', value: 96 }
]

const totalPages = computed(() => {
  return Math.ceil(props.total / props.pageSize)
})

const startItem = computed(() => {
  if (props.total === 0) return 0
  return (props.page - 1) * props.pageSize + 1
})

const endItem = computed(() => {
  const end = props.page * props.pageSize
  return end > props.total ? props.total : end
})

const handlePageChange = (newPage: number) => {
  emit('update:page', newPage)
  // Scroll to top when page changes
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handlePageSizeChange = (newSize: number) => {
  emit('update:page-size', newSize)
  // Reset to first page when page size changes
  emit('update:page', 1)
}
</script>

<style scoped>
.pagination-controls {
  padding: 24px 0;
}

.page-size-select {
  max-width: 80px;
}
</style>
