<template>
  <div class="pet-sorting d-flex align-center">
    <span class="text-body-2 text-medium-emphasis mr-2">排序：</span>
    <v-select
      :model-value="sortBy"
      :items="sortOptions"
      density="compact"
      variant="outlined"
      hide-details
      class="sort-select"
      @update:model-value="handleSortChange"
    >
      <template #selection="{ item }">
        <div class="d-flex align-center">
          <v-icon :icon="item.raw.icon" size="small" class="mr-1" />
          <span>{{ item.title }}</span>
        </div>
      </template>
      <template #item="{ item, props: itemProps }">
        <v-list-item v-bind="itemProps">
          <template #prepend>
            <v-icon :icon="item.raw.icon" />
          </template>
        </v-list-item>
      </template>
    </v-select>
  </div>
</template>

<script setup lang="ts">
interface SortOption {
  title: string
  value: string
  icon: string
}

interface Props {
  sortBy: string
}

defineProps<Props>()

const emit = defineEmits<{
  'update:sort-by': [value: string]
}>()

const sortOptions: SortOption[] = [
  {
    title: '請選擇排序',
    value: 'random',
    icon: 'mdi-shuffle-variant'
  },
  {
    title: '最新上架',
    value: 'newest',
    icon: 'mdi-clock-outline'
  },
  {
    title: '年齡 (小到大)',
    value: 'age_asc',
    icon: 'mdi-sort-ascending'
  },
  {
    title: '年齡 (大到小)',
    value: 'age_desc',
    icon: 'mdi-sort-descending'
  },
  {
    title: '名稱 (A-Z)',
    value: 'name_asc',
    icon: 'mdi-sort-alphabetical-ascending'
  },
  {
    title: '名稱 (Z-A)',
    value: 'name_desc',
    icon: 'mdi-sort-alphabetical-descending'
  }
]

const handleSortChange = (value: string) => {
  emit('update:sort-by', value)
}
</script>

<style scoped>
.pet-sorting {
  min-width: 250px;
}

.sort-select {
  max-width: 200px;
}
</style>
