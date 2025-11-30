<template>
  <AppHeader/>
  <v-container style="margin-top: 70px;">
    <v-row>
      <v-col cols="12">
        <!-- Page Header -->
        <div class="d-flex align-center mb-6">
          <v-btn
            icon="mdi-arrow-left"
            variant="text"
            @click="goBack"
          />
          <div class="ml-4">
            <h1 class="text-h4">文件上傳</h1>
            <p class="text-body-2 text-grey mt-1">
              請上傳認養申請所需的相關文件
            </p>
          </div>
        </div>

        <!-- Application Info -->
        <v-alert
          v-if="applicationId"
          type="info"
          variant="tonal"
          class="mb-6"
        >
          <div class="d-flex align-center">
            <div>
              <p class="mb-1">申請編號：#{{ applicationId }}</p>
              <p class="text-caption mb-0">
                上傳所需文件後，即可繼續下一步完成申請
              </p>
            </div>
          </div>
        </v-alert>

        <!-- Upload Section -->
        <v-row>
          <v-col cols="12" lg="8">
            <DocumentUploader
              :application-id="applicationId"
              @upload-success="handleUploadSuccess"
              @upload-complete="handleUploadComplete"
            />
          </v-col>

          <!-- Quick Info Sidebar -->
          <v-col cols="12" lg="4">
            <v-card>
              <v-card-title>
                <v-icon left>mdi-help-circle</v-icon>
                上傳指南
              </v-card-title>
              <v-divider />
              <v-card-text>
                <v-list density="compact">
                  <v-list-item prepend-icon="mdi-check">
                    <v-list-item-title>支援格式</v-list-item-title>
                    <v-list-item-subtitle>
                      PDF, JPG, PNG, DOC, DOCX, TXT
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item prepend-icon="mdi-file-check">
                    <v-list-item-title>檔案大小</v-list-item-title>
                    <v-list-item-subtitle>
                      單檔上限 10MB
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item prepend-icon="mdi-upload">
                    <v-list-item-title>即時上傳</v-list-item-title>
                    <v-list-item-subtitle>
                      上傳完成後即可繼續申請
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>

                <v-divider class="my-4" />

                <h4 class="text-subtitle-2 mb-2">必要文件說明</h4>
                <v-expansion-panels variant="accordion">
                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon left size="small">mdi-card-account-details</v-icon>
                      身分證明
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      請提供身分證正反面影本或其他有效身分證明文件
                    </v-expansion-panel-text>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon left size="small">mdi-cash</v-icon>
                      收入證明
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      薪資單、扣繳憑單或其他收入證明文件，以評估飼養能力
                    </v-expansion-panel-text>
                  </v-expansion-panel>

                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon left size="small">mdi-home</v-icon>
                      居住證明
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      戶籍謄本、租賃合約或其他居住地證明文件
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Uploaded Documents Section -->
        <v-row class="mt-6">
          <v-col cols="12">
            <UploadedDocuments
              ref="uploadedDocumentsRef"
              :application-id="applicationId"
              @document-deleted="handleDocumentDeleted"
              @replace-document="handleReplaceDocument"
            />
          </v-col>
        </v-row>

        <!-- Action Buttons -->
        <v-row class="mt-6">
          <v-col cols="12" class="d-flex justify-end gap-x-6">
            <v-btn
              color="grey"
              variant="outlined"
              class="me-4"
              @click="goBack"
            >
              返回
            </v-btn>
            <v-btn
              color="primary"
              variant="flat"
              @click="proceedToNext"
              :disabled="!canProceed"
            >
              送出文件
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import DocumentUploader from '@/components/upload/DocumentUploader.vue'
import UploadedDocuments from '@/components/upload/UploadedDocuments.vue'
import { getDocumentList } from '@/api/document'
import type { DocumentResponse, DocumentListResponse } from '@/types/document'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()
const route = useRoute()

const applicationId = computed(() => {
  return parseInt(route.params.applicationId as string)
})

const uploadedDocumentsRef = ref<InstanceType<typeof UploadedDocuments>>()
const documentList = ref<DocumentListResponse | null>(null)
const canProceed = ref(false)

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

onMounted(async () => {
  await checkDocumentCompletion()
})

async function checkDocumentCompletion() {
  try {
    documentList.value = await getDocumentList(applicationId.value)
    // 只要有上傳文件就可以繼續，不需要等待審核
    canProceed.value = (documentList.value.documents?.length || 0) > 0
  } catch (error) {
    console.error('Failed to check document completion:', error)
  }
}

function handleUploadSuccess(document: DocumentResponse) {
  showSnackbar(`成功上傳：${document.original_filename}`, 'success')
  uploadedDocumentsRef.value?.loadDocuments()
  checkDocumentCompletion()
}

function handleUploadComplete(results: { success: number; failed: number }) {
  if (results.failed === 0) {
    showSnackbar(`成功上傳 ${results.success} 個檔案`, 'success')
  } else {
    showSnackbar(
      `上傳完成：${results.success} 個成功，${results.failed} 個失敗`,
      'warning'
    )
  }
}

function handleDocumentDeleted() {
  showSnackbar('文件已刪除', 'success')
  checkDocumentCompletion()
}

function handleReplaceDocument(doc: DocumentResponse) {
  // Scroll to uploader
  window.scrollTo({ top: 0, behavior: 'smooth' })
  showSnackbar(`請上傳新的${doc.document_type}文件以替換`, 'info')
}

function showSnackbar(message: string, color: string) {
  snackbar.value = {
    show: true,
    message,
    color
  }
}

function goBack() {
  router.back()
}

function proceedToNext() {
  // Navigate to application status page
  router.push({
    name: 'ApplicationStatus',
    params: { applicationId: applicationId.value }
  })
}
</script>

<style scoped>
/* Add any page-specific styles here */
</style>
