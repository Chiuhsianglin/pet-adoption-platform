<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="80vw"
    scrollable
  >
    <v-card v-if="petId" style="max-height: 80vh;">
      <v-toolbar color="primary" dark>
        <v-toolbar-title>寵物詳情</v-toolbar-title>
        <v-spacer />
        <v-btn icon="mdi-open-in-new" @click="openInNewTab" />
        <v-btn icon="mdi-close" @click="$emit('update:modelValue', false)" />
      </v-toolbar>
      <v-card-text class="pa-0">
        <v-container>
          <PetDetailContent :pet-id="petId" @close="$emit('update:modelValue', false)" />
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import PetDetailContent from './PetDetailContent.vue'

const props = defineProps<{
  modelValue: boolean
  petId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const openInNewTab = () => {
  if (props.petId) {
    window.open(`/pets/${props.petId}`, '_blank')
  }
}
</script>
