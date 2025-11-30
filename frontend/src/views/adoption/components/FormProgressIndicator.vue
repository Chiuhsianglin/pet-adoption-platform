<template>
  <div class="form-progress">
    <div class="steps">
      <div
        v-for="step in steps"
        :key="step.number"
        class="step"
        :class="{
          active: step.number === currentStep,
          completed: step.number < currentStep
        }"
      >
        <div class="step-circle">
          <v-icon v-if="step.number < currentStep">mdi-check</v-icon>
          <span v-else>{{ step.number }}</span>
        </div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FormStep } from '@/types/adoption'

interface Props {
  currentStep: FormStep
}

const props = defineProps<Props>()

const steps = [
  { number: 1, label: '個人資訊' },
  { number: 2, label: '居住環境' },
  { number: 3, label: '養寵經驗' },
  { number: 4, label: '確認送出' }
]

const progressPercent = computed(() => {
  return ((props.currentStep - 1) / (steps.length - 1)) * 100
})
</script>

<style scoped>
.form-progress {
  margin-bottom: 2rem;
}

.steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  position: relative;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #757575;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.3s;
  z-index: 1;
}

.step.active .step-circle {
  background: #FF6B6B;
  color: white;
}

.step.completed .step-circle {
  background: #f5c94e;
  color: white;
}

.step-label {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #757575;
  transition: color 0.3s;
}

.step.active .step-label {
  color: #FF6B6B;
  font-weight: 600;
}

.step.completed .step-label {
  color: #f5c94e  ;
}

.progress-bar {
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B6B, #ffe398);
  transition: width 0.3s ease;
}

@media (max-width: 600px) {
  .step-label {
    font-size: 0.75rem;
  }

  .step-circle {
    width: 32px;
    height: 32px;
    font-size: 0.875rem;
  }
}
</style>
