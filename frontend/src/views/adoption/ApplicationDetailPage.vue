<template>
  <v-app>
    <AppHeader />
    <v-main>
      <v-container class="py-8" style="max-width: 1200px;">
        <!-- Loading State -->
        <v-skeleton-loader
          v-if="loading"
          type="article, article, article"
        />

        <!-- Error State -->
        <v-alert
          v-else-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
        >
          {{ error }}
          <template #append>
            <v-btn
              color="error"
              variant="text"
              @click="$router.back()"
            >
              返回
            </v-btn>
          </template>
        </v-alert>

        <!-- Application Detail -->
        <div v-else-if="application">
          <!-- Header with Status -->
          <div class="d-flex align-center mb-6">
            <v-btn
              icon="mdi-arrow-left"
              variant="text"
              @click="$router.back()"
            />
            <h1 class="text-h4 ml-2">申請詳情與審核 #{{ application.id }}</h1>
            <v-spacer />
            <v-chip
              :color="getStatusColor(application.status)"
              size="large"
              class="px-4"
            >
              {{ getStatusText(application.status) }}
            </v-chip>
          </div>

          <!-- Home Visit Info & Actions (if scheduled) -->
          <v-card class="mb-4" v-if="isShelter && ['home_visit_scheduled', 'home_visit_completed', 'under_evaluation', 'approved', 'rejected'].includes(application.status)" :color="getHomeVisitCardColor(application.status)" variant="tonal">
            <v-card-title class="d-flex align-center">
              <v-icon start>{{ getHomeVisitCardIcon(application.status) }}</v-icon>
              {{ getHomeVisitCardTitle(application.status) }}
            </v-card-title>
            <v-card-text class="pa-4">
              <v-row dense>
                <v-col cols="12" sm="6" v-if="application.home_visit_date">
                  <div class="text-caption text-grey mb-1">家訪日期</div>
                  <div class="text-body-1">{{ formatDateTime(application.home_visit_date) }}</div>
                </v-col>
                <v-col cols="12" v-if="!application.home_visit_date && application.status === 'home_visit_scheduled'">
                  <v-alert type="warning" variant="tonal" class="mb-0">
                    <div class="text-body-2">請安排家訪日期時間</div>
                  </v-alert>
                </v-col>
                <v-col cols="12" v-if="application.home_visit_notes">
                  <div class="text-caption text-grey mb-1">家訪記錄</div>
                  <div class="text-body-1" style="white-space: pre-wrap;">{{ application.home_visit_notes }}</div>
                </v-col>
                <v-col cols="12" v-if="application.home_visit_document">
                  <div class="text-caption text-grey mb-1">家訪文件</div>
                  <v-btn
                    :href="application.home_visit_document"
                    target="_blank"
                    variant="outlined"
                    color="primary"
                    size="small"
                  >
                    <v-icon start>mdi-file-document</v-icon>
                    查看文件
                  </v-btn>
                </v-col>
                <v-col cols="12" v-if="application.final_decision_notes && (application.status === 'approved' || application.status === 'rejected')">
                  <v-divider class="my-2" />
                  <div class="text-caption text-grey mb-1">{{ application.status === 'approved' ? '審核備註' : '拒絕原因' }}</div>
                  <div class="text-body-1" style="white-space: pre-wrap;">{{ application.final_decision_notes }}</div>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions class="pa-4" v-if="application.status === 'home_visit_scheduled'">
              <v-spacer />
              <!-- Schedule Home Visit Date if not set -->
              <v-btn
                v-if="!application.home_visit_date"
                color="primary"
                variant="elevated"
                size="large"
                @click="openScheduleHomeVisitDialog"
              >
                <v-icon start>mdi-calendar-clock</v-icon>
                安排家訪日期
              </v-btn>
              
              <!-- Reschedule Home Visit if date is set -->
              <v-btn
                v-if="application.home_visit_date"
                color="secondary"
                variant="outlined"
                size="large"
                @click="openRescheduleHomeVisitDialog"
              >
                <v-icon start>mdi-calendar-edit</v-icon>
                修改家訪時間
              </v-btn>

              <!-- Complete Home Visit (only if date is set) -->
              <v-btn
                v-if="application.home_visit_date"
                color="info"
                variant="elevated"
                size="large"
                @click="openCompleteHomeVisitDialog"
              >
                <v-icon start class="me-1">mdi-home-account</v-icon>
                完成家訪
              </v-btn>
            </v-card-actions>
            <v-card-actions class="pa-4" v-if="application.status === 'home_visit_completed' || application.status === 'under_evaluation'">
              <v-spacer />
              <!-- Edit Home Visit Record -->
              <v-btn
                color="secondary"
                variant="outlined"
                size="large"
                @click="openEditHomeVisitDialog"
              >
                <v-icon start>mdi-pencil</v-icon>
                修改家訪紀錄
              </v-btn>
            </v-card-actions>
          </v-card>

          <!-- Pet Info Card -->
          <v-card class="mb-4">
            <v-card-title class="bg-primary text-white d-flex align-center">
              <v-icon start>mdi-paw</v-icon>
              申請領養的寵物
            </v-card-title>
            <v-card-text class="pa-4">
              <v-row>
                <v-col cols="12" md="3">
                  <v-img
                    v-if="application.pet?.photos?.[0]"
                    :src="getPhotoUrl(application.pet.photos[0])"
                    aspect-ratio="1"
                    cover
                    class="rounded"
                  />
                  <div v-else class="d-flex align-center justify-center bg-grey-lighten-3 rounded" style="aspect-ratio: 1">
                    <v-icon size="80" color="grey">mdi-paw</v-icon>
                  </div>
                </v-col>
                <v-col cols="12" md="9">
                  <h3 class="text-h5 mb-4">{{ application.pet?.name || '未知寵物' }}</h3>
                  <v-row dense>
                    <v-col cols="6" sm="3">
                      <div class="text-caption text-grey mb-1">品種</div>
                      <div class="text-body-1">{{ application.pet?.breed }}</div>
                    </v-col>
                    <v-col cols="6" sm="3">
                      <div class="text-caption text-grey mb-1">年齡</div>
                      <div class="text-body-1">{{ calculateAge(application.pet?.age_years, application.pet?.age_months) }}</div>
                    </v-col>
                    <v-col cols="6" sm="3">
                      <div class="text-caption text-grey mb-1">性別</div>
                      <div class="text-body-1">{{ genderLabel(application.pet?.gender) }}</div>
                    </v-col>
                    <v-col cols="6" sm="3">
                      <div class="text-caption text-grey mb-1">體型</div>
                      <div class="text-body-1">{{ sizeLabel(application.pet?.size) }}</div>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Personal Info -->
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-4 d-flex align-center">
              <v-icon start>mdi-account</v-icon>
              個人資訊
            </v-card-title>
            <v-card-text class="pa-4">
              <v-row dense>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">姓名</div>
                  <div class="text-body-1">{{ application.personal_info?.name || application.user?.name }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">電話</div>
                  <div class="text-body-1">{{ application.personal_info?.phone || application.user?.phone }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">Email</div>
                  <div class="text-body-1">{{ application.personal_info?.email || application.user?.email }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">身份證</div>
                  <div class="text-body-1">{{ application.personal_info?.id_number || '-' }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">職業</div>
                  <div class="text-body-1">{{ application.personal_info?.occupation || '-' }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">月收入</div>
                  <div class="text-body-1">NT$ {{ formatIncome(application.personal_info?.monthly_income) }}</div>
                </v-col>
                <v-col cols="12">
                  <div class="text-caption text-grey mb-1">地址</div>
                  <div class="text-body-1">{{ application.personal_info?.address || application.user?.address || '-' }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Living Environment -->
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-4 d-flex align-center">
              <v-icon start>mdi-home</v-icon>
              居住環境
            </v-card-title>
            <v-card-text class="pa-4">
              <v-row dense>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">住宅類型</div>
                  <div class="text-body-1">{{ housingTypeLabel(application.living_environment?.housing_type) }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">空間大小</div>
                  <div class="text-body-1">{{ application.living_environment?.space_size || '-' }} 坪</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">院子/陽台</div>
                  <div class="text-body-1">{{ application.living_environment?.has_yard ? '有' : '無' }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">家庭成員</div>
                  <div class="text-body-1">{{ application.living_environment?.family_members || '-' }} 人</div>
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <div class="text-caption text-grey mb-1">過敏史</div>
                  <div class="text-body-1">{{ application.living_environment?.has_allergies ? '有' : '無' }}</div>
                </v-col>
                
                <!-- Other Pets -->
                <v-col cols="12" v-if="application.living_environment?.other_pets?.length > 0">
                  <div class="text-caption text-grey mb-2">其他寵物</div>
                  <v-list density="compact" class="bg-grey-lighten-5 rounded">
                    <v-list-item
                      v-for="(pet, idx) in application.living_environment.other_pets"
                      :key="idx"
                    >
                      <v-list-item-title>
                        {{ pet.species }} ({{ pet.age }} 歲) - {{ pet.vaccinated ? '已施打疫苗' : '未施打疫苗' }}
                      </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-col>

                <!-- Environment Photos -->
                <v-col cols="12" v-if="application.living_environment?.environment_photos?.length > 0">
                  <div class="text-caption text-grey mb-2">居住環境照片</div>
                  <v-row>
                    <v-col
                      v-for="(photo, idx) in application.living_environment.environment_photos"
                      :key="idx"
                      cols="6"
                      sm="4"
                      md="3"
                    >
                      <v-img
                        :src="getPhotoUrl(photo)"
                        aspect-ratio="1"
                        cover
                        class="rounded"
                        @click="openImageViewer(getPhotoUrl(photo))"
                        style="cursor: pointer;"
                      />
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Pet Experience -->
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-4 d-flex align-center">
              <v-icon start>mdi-paw-outline</v-icon>
              養寵經驗
            </v-card-title>
            <v-card-text class="pa-4">
              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-2">過往經驗</div>
                <div class="text-body-1" style="white-space: pre-wrap;">{{ application.pet_experience?.previous_experience || '-' }}</div>
              </div>
              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-2">寵物了解</div>
                <div class="text-body-1" style="white-space: pre-wrap;">{{ application.pet_experience?.pet_knowledge || '-' }}</div>
              </div>
              <div class="mb-4">
                <div class="text-subtitle-2 text-grey mb-2">照護計劃</div>
                <div class="text-body-1" style="white-space: pre-wrap;">{{ application.pet_experience?.care_schedule || '-' }}</div>
              </div>
              <v-row dense>
                <v-col cols="12" sm="6">
                  <div class="text-caption text-grey mb-1">獸醫資訊</div>
                  <div class="text-body-1">{{ application.pet_experience?.veterinarian_info || '-' }}</div>
                </v-col>
                <v-col cols="12" sm="6">
                  <div class="text-caption text-grey mb-1">緊急費用準備</div>
                  <div class="text-body-1">NT$ {{ formatIncome(application.pet_experience?.emergency_fund) }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Uploaded Documents -->
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-4 d-flex align-center">
              <v-icon start>mdi-file-document</v-icon>
              申請者上傳文件
            </v-card-title>
            <v-card-text class="pa-4">
              <v-list v-if="application.documents && application.documents.length > 0" density="compact">
                <v-list-item
                  v-for="doc in application.documents"
                  :key="doc.id"
                >
                  <template #prepend>
                    <!-- 如果是圖片，顯示縮圖預覽 -->
                    <v-avatar v-if="isImageFile(doc)" size="48" rounded="lg" class="mr-2">
                      <v-img :src="getDocumentUrl(doc)" cover />
                    </v-avatar>
                    <v-icon v-else color="primary">mdi-file-document-outline</v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium">{{ getDocumentTypeName(doc.document_type) }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ doc.original_filename || doc.file_name }}
                    <br>
                    上傳時間：{{ formatDate(doc.uploaded_at) }}
                  </v-list-item-subtitle>
                  <template #append>
                    <!-- 如果是圖片，提供查看和下載按鈕 -->
                    <div v-if="isImageFile(doc)" class="d-flex ga-1">
                      <v-btn
                        icon="mdi-eye"
                        variant="text"
                        size="small"
                        color="primary"
                        @click="openImageViewer(getDocumentUrl(doc))"
                      />
                      <v-btn
                        icon="mdi-download"
                        variant="text"
                        size="small"
                        color="primary"
                        :href="getDocumentUrl(doc)"
                        target="_blank"
                        download
                      />
                    </div>
                    <!-- 如果是 PDF 或其他文件，提供查看和下載按鈕 -->
                    <div v-else class="d-flex ga-1">
                      <v-btn
                        icon="mdi-open-in-new"
                        variant="text"
                        size="small"
                        color="primary"
                        :href="getDocumentUrl(doc)"
                        target="_blank"
                      />
                      <v-btn
                        icon="mdi-download"
                        variant="text"
                        size="small"
                        color="primary"
                        :href="getDocumentUrl(doc)"
                        download
                      />
                    </div>
                  </template>
                </v-list-item>
              </v-list>
              <v-alert
                v-else
                type="warning"
                variant="tonal"
                density="compact"
              >
                <div class="d-flex align-center justify-space-between">
                  <span>申請者尚未上傳任何文件</span>
                  <!--<v-btn
                    v-if="isShelter && ['submitted', 'document_review'].includes(application.status)"
                    color="warning"
                    variant="elevated"
                    size="small"
                    @click="requestDocuments"
                    :loading="requestingDocuments"
                  >
                    <v-icon start>mdi-file-alert</v-icon>
                    通知補件
                  </v-btn>-->
                </div>
              </v-alert>
            </v-card-text>
          </v-card>

          <!-- Final Decision Notes -->
          <v-card class="mb-4" v-if="application.final_decision_notes" :color="application.status === 'approved' ? 'success' : 'error'" variant="tonal">
            <v-card-title class="d-flex align-center">
              <v-icon start>mdi-clipboard-check</v-icon>
              最終決定備註
            </v-card-title>
            <v-card-text class="pa-4">
              <div class="text-body-1" style="white-space: pre-wrap;">{{ application.final_decision_notes }}</div>
            </v-card-text>
          </v-card>

          <!-- Action Buttons for Shelter -->
          <v-card v-if="isShelter">
            <v-card-actions class="pa-4 d-flex flex-wrap ga-2">
              <v-btn
                variant="text"
                @click="$router.back()"
              >
                返回列表
              </v-btn>
              <v-spacer />
              
              <!-- Request Documents if no documents uploaded -->
              <v-btn
                v-if="['submitted', 'document_review'].includes(application.status) && (!application.documents || application.documents.length === 0)"
                color="warning"
                variant="elevated"
                size="large"
                @click="requestDocuments"
                :loading="requestingDocuments"
              >
                <v-icon start>mdi-file-alert</v-icon>
                通知補件
              </v-btn>
              
              <!-- Schedule Home Visit if documents uploaded -->
              <v-btn
                v-if="['submitted', 'document_review'].includes(application.status) && application.documents && application.documents.length > 0"
                color="primary"
                variant="elevated"
                size="large"
                @click="openScheduleHomeVisitDialog"
              >
                <v-icon start>mdi-calendar-clock</v-icon>
                安排家訪
              </v-btn>

              <!-- Final Decision Buttons -->
              <v-btn
                v-if="['home_visit_completed', 'under_evaluation'].includes(application.status)"
                color="success"
                variant="elevated"
                size="large"
                @click="openFinalDecisionDialog(true)"
              >
                <v-icon start>mdi-check-circle</v-icon>
                通過申請
              </v-btn>
              
              <v-btn
                v-if="['home_visit_completed', 'under_evaluation'].includes(application.status)"
                color="error"
                variant="elevated"
                size="large"
                @click="openFinalDecisionDialog(false)"
              >
                <v-icon start>mdi-close-circle</v-icon>
                拒絕申請
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>

        <!-- Request Documents Dialog -->
        <v-dialog v-model="requestDocumentsDialog" max-width="500">
          <v-card>
            <v-card-title class="bg-warning text-white d-flex align-center">
              <v-icon start color="white">mdi-file-alert</v-icon>
              通知申請者補充文件
            </v-card-title>
            <v-card-text class="py-4">
              <v-alert type="info" variant="tonal" class="mb-4">
                <div class="text-body-1">
                  系統將發送通知給申請者，提醒其上傳所需文件。
                </div>
              </v-alert>
              <div class="text-body-2 text-grey-darken-1">
                通知內容：
              </div>
              <div class="bg-grey-lighten-4 pa-3 rounded mt-2">
                <div class="text-body-2">
                  <strong>標題：</strong>請補充申請文件
                </div>
                <div class="text-body-2 mt-2">
                  <strong>內容：</strong>您的申請文件（申請編號 #{{ application?.id }}）尚未上傳完整。請至「我的申請」頁面上傳所需文件，以便我們進行審核。感謝您的配合！
                </div>
              </div>
            </v-card-text>
            <v-card-actions class="px-4 pb-4">
              <v-spacer />
              <v-btn variant="text" @click="requestDocumentsDialog = false">取消</v-btn>
              <v-btn
                color="warning"
                variant="elevated"
                :loading="requestingDocuments"
                @click="confirmRequestDocuments"
              >
                <v-icon start>mdi-send</v-icon>
                發送通知
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Schedule Home Visit Dialog -->
        <v-dialog v-model="scheduleHomeVisitDialog" max-width="500">
          <v-card>
            <v-card-title>
              <v-icon start color="primary">mdi-calendar-clock</v-icon>
              {{ application?.home_visit_date ? '修改家訪時間' : '安排家訪日期' }}
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="homeVisitDate"
                label="家訪日期時間"
                type="datetime-local"
                variant="outlined"
                density="comfortable"
                color="primary"
                hint="請選擇家訪的日期和時間"
                persistent-hint
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn variant="text" @click="scheduleHomeVisitDialog = false">取消</v-btn>
              <v-btn
                color="primary"
                variant="elevated"
                :loading="submitting"
                @click="scheduleHomeVisit"
              >
                {{ application?.home_visit_date ? '確認修改' : '確認安排' }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Complete Home Visit Dialog -->
        <v-dialog v-model="completeHomeVisitDialog" max-width="600">
          <v-card>
            <v-card-title>
              <v-icon start color="primary">mdi-home-account</v-icon>
              完成家訪記錄
            </v-card-title>
            <v-card-text>
              <v-textarea
                v-model="homeVisitNotes"
                label="家訪記錄"
                variant="outlined"
                rows="5"
                hint="請記錄家訪的觀察與評估"
                persistent-hint
                class="mb-4"
              />
              <v-file-input
                v-model="homeVisitDocument"
                label="家訪文件（選填）"
                variant="outlined"
                prepend-icon="mdi-paperclip"
                hint="可上傳照片或相關文件"
                persistent-hint
                accept="image/*,application/pdf"
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn variant="text" @click="completeHomeVisitDialog = false">取消</v-btn>
              <v-btn
                color="primary"
                variant="elevated"
                :loading="submitting"
                @click="completeHomeVisit"
              >
                完成家訪
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Final Decision Dialog -->
        <v-dialog v-model="finalDecisionDialog" max-width="600">
          <v-card>
            <v-card-title>
              <v-icon start :color="isApproving ? 'success' : 'error'">
                {{ isApproving ? 'mdi-check-circle' : 'mdi-close-circle' }}
              </v-icon>
              {{ isApproving ? '通過申請' : '拒絕申請' }}
            </v-card-title>
            <v-card-text>
              <v-textarea
                v-model="finalDecisionNotes"
                :label="isApproving ? '通過備註（例如：聯絡事項）' : '拒絕原因'"
                variant="outlined"
                rows="5"
                :hint="isApproving ? '請提供後續聯絡事項或注意事項' : '請說明拒絕的原因'"
                persistent-hint
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn variant="text" @click="finalDecisionDialog = false">取消</v-btn>
              <v-btn
                :color="isApproving ? 'success' : 'error'"
                variant="elevated"
                :loading="submitting"
                @click="makeFinalDecision"
              >
                確認{{ isApproving ? '通過' : '拒絕' }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Success Dialog -->
        <v-dialog v-model="successDialog" max-width="400">
          <v-card>
            <v-card-title class="text-center py-4">
              <v-icon size="64" color="success">mdi-check-circle</v-icon>
            </v-card-title>
            <v-card-text class="text-center pb-2">
              <h3 class="text-h5 mb-2">{{ successMessage }}</h3>
              <p class="text-body-1">{{ successDetails }}</p>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn
                color="primary"
                variant="elevated"
                @click="successDialog = false"
              >
                確定
              </v-btn>
              <v-spacer />
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Pet Unavailable Dialog -->
        <v-dialog v-model="petUnavailableDialog" max-width="600" persistent>
          <v-card>
            <v-card-title class="bg-error text-white d-flex align-center">
              <v-icon color="white" class="mr-2">mdi-alert-circle</v-icon>
              寵物已不可領養
            </v-card-title>
            <v-card-text class="py-4">
              <v-alert type="warning" variant="tonal" class="mb-4">
                <div class="text-body-1">
                  <strong>{{ petUnavailableInfo.pet_name }}</strong> 目前狀態為：
                  <v-chip size="small" class="ml-2" color="warning">
                    {{ petUnavailableInfo.pet_status }}
                  </v-chip>
                </div>
                <div class="mt-2">
                  由於寵物已不可領養，無法繼續審核此申請。請輸入拒絕原因通知申請者。
                </div>
              </v-alert>
              
              <v-textarea
                v-model="rejectionReason"
                label="拒絕原因（必填）"
                placeholder="例如：很抱歉，此寵物已被其他申請者領養。"
                rows="4"
                variant="outlined"
                :rules="[(v) => !!v || '請輸入拒絕原因']"
              />
            </v-card-text>
            <v-card-actions class="px-4 pb-4">
              <v-btn
                variant="text"
                @click="closePetUnavailableDialog"
                :disabled="submitting"
              >
                取消
              </v-btn>
              <v-spacer />
              <v-btn
                color="error"
                variant="elevated"
                @click="rejectApplicationDueToPetUnavailable"
                :loading="submitting"
                :disabled="!rejectionReason.trim()"
              >
                通知申請者
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { calculateAge } from '@/utils/ageCalculator'
import AppHeader from '@/components/layout/AppHeader.vue'
import api from '@/services/api'
import { useNotificationStore } from '@/stores/notification'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()
const authStore = useAuthStore()

const application = ref<any>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const submitting = ref(false)

// Dialogs
const scheduleHomeVisitDialog = ref(false)
const completeHomeVisitDialog = ref(false)
const finalDecisionDialog = ref(false)
const successDialog = ref(false)
const successMessage = ref('')
const successDetails = ref('')
const petUnavailableDialog = ref(false)
const petUnavailableInfo = ref({ pet_status: '', pet_name: '' })
const rejectionReason = ref('')
const requestingDocuments = ref(false)
const requestDocumentsDialog = ref(false)

// Form data
const homeVisitDate = ref('')
const homeVisitNotes = ref('')
const homeVisitDocument = ref<File[] | null>(null)
const finalDecisionNotes = ref('')
const isApproving = ref(false)

const isShelter = computed(() => authStore.user?.role === 'shelter')

// Helper functions for home visit card
function getHomeVisitCardColor(status: string): string {
  if (status === 'approved' || status === 'completed') return 'success'
  if (status === 'rejected') return 'error'
  if (status === 'home_visit_completed' || status === 'under_evaluation') return 'success'
  return 'info'
}

function getHomeVisitCardIcon(status: string): string {
  if (status === 'approved' || status === 'completed') return 'mdi-check-circle'
  if (status === 'rejected') return 'mdi-close-circle'
  return 'mdi-home-account'
}

function getHomeVisitCardTitle(status: string): string {
  if (status === 'approved') return '領養申請通過'
  if (status === 'rejected') return '領養申請拒絕'
  if (status === 'completed') return '領養已完成'
  if (status === 'home_visit_completed' || status === 'under_evaluation') return '已完成家訪'
  return '已安排家訪'
}

onMounted(() => {
  loadApplication()
})

const loadApplication = async () => {
  loading.value = true
  error.value = null
  try {
    const applicationId = route.params.id
    const response = await api.get(`/adoptions/applications/${applicationId}`)
    console.log('📋 Application data received:', response.data)
    console.log('🐾 Pet data:', response.data.pet)
    application.value = response.data
  } catch (err: any) {
    console.error('Failed to load application:', err)
    error.value = err.response?.data?.detail || '載入申請失敗'
  } finally {
    loading.value = false
  }
}

// Schedule Home Visit
const openScheduleHomeVisitDialog = () => {
  // 先檢查寵物是否為 AVAILABLE 狀態
  if (application.value?.pet?.status !== 'available') {
    petUnavailableInfo.value = {
      pet_status: getPetStatusText(application.value?.pet?.status),
      pet_name: application.value?.pet?.name || '未知寵物'
    }
    petUnavailableDialog.value = true
    return
  }
  
  homeVisitDate.value = ''
  scheduleHomeVisitDialog.value = true
}

// Reschedule Home Visit (reuse the same dialog)
const openRescheduleHomeVisitDialog = () => {
  // Pre-fill with current home visit date
  if (application.value?.home_visit_date) {
    const date = new Date(application.value.home_visit_date)
    // Format to local datetime-local format (YYYY-MM-DDTHH:mm)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    homeVisitDate.value = `${year}-${month}-${day}T${hours}:${minutes}`
  } else {
    homeVisitDate.value = ''
  }
  scheduleHomeVisitDialog.value = true
}

const scheduleHomeVisit = async () => {
  if (!homeVisitDate.value) {
    notificationStore.error('請選擇家訪日期時間')
    return
  }

  submitting.value = true
  try {
    // 判斷是新建還是修改
    const isRescheduling = application.value?.home_visit_date != null
    
    if (isRescheduling) {
      // 修改家訪時間 - 使用 PUT
      await api.put(
        `/adoptions/applications/${application.value!.id}/home-visit-date`,
        {
          home_visit_date: homeVisitDate.value
        }
      )
    } else {
      // 安排家訪 - 使用 POST
      await api.post(
        `/adoptions/applications/${application.value!.id}/schedule-home-visit`,
        {
          home_visit_date: homeVisitDate.value
        }
      )
    }
    
    scheduleHomeVisitDialog.value = false
    await loadApplication()
    
    // Show success dialog
    const isReschedule = application.value?.home_visit_date
    successMessage.value = isReschedule ? '已修改家訪時間' : '家訪已安排'
    successDetails.value = `家訪日期：${formatDateTime(homeVisitDate.value.replace('T', ' '))}`
    successDialog.value = true
  } catch (err: any) {
    console.error('Failed to schedule home visit:', err)
    notificationStore.error(err.response?.data?.detail || '安排家訪失敗')
  } finally {
    submitting.value = false
  }
}

// Complete Home Visit
const openCompleteHomeVisitDialog = () => {
  homeVisitNotes.value = ''
  homeVisitDocument.value = null
  completeHomeVisitDialog.value = true
}

const openEditHomeVisitDialog = () => {
  // Pre-fill with existing data
  homeVisitNotes.value = application.value?.home_visit_notes || ''
  homeVisitDocument.value = null
  completeHomeVisitDialog.value = true
}

const completeHomeVisit = async () => {
  if (!homeVisitNotes.value) {
    notificationStore.error('請填寫家訪記錄')
    return
  }

  submitting.value = true
  try {
    console.log('🔍 homeVisitDocument.value:', homeVisitDocument.value)
    console.log('🔍 homeVisitDocument type:', typeof homeVisitDocument.value)
    console.log('🔍 Is array?:', Array.isArray(homeVisitDocument.value))
    
    // 判斷是完成家訪還是修改紀錄
    const isEditing = application.value?.home_visit_notes != null
    
    const formData = new FormData()
    formData.append('notes', homeVisitNotes.value)
    
    // Handle both single file and array formats
    let fileToUpload: File | null = null
    
    if (homeVisitDocument.value) {
      if (Array.isArray(homeVisitDocument.value) && homeVisitDocument.value.length > 0) {
        fileToUpload = homeVisitDocument.value[0]
      } else if (homeVisitDocument.value instanceof File) {
        fileToUpload = homeVisitDocument.value as File
      }
    }
    
    if (fileToUpload) {
      console.log('📄 Uploading home visit document:', fileToUpload)
      console.log('📄 Document name:', fileToUpload.name)
      console.log('📄 Document size:', fileToUpload.size)
      console.log('📄 Document type:', fileToUpload.type)
      formData.append('document', fileToUpload)
    } else {
      console.log('⚠️ No document to upload')
    }
    
    // Log FormData contents
    console.log('📦 FormData entries:')
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value)
    }

    let response
    if (isEditing) {
      // 修改家訪紀錄 - 使用 PUT
      console.log('📝 Updating home visit record (PUT)')
      response = await api.put(
        `/adoptions/applications/${application.value!.id}/home-visit-record`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
    } else {
      // 完成家訪 - 使用 POST
      console.log('🏠 Completing home visit (POST)')
      response = await api.post(
        `/adoptions/applications/${application.value!.id}/complete-home-visit`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
    }
    
    console.log('✅ Home visit response:', response.data)
    
    notificationStore.success(isEditing ? '家訪記錄已更新' : '家訪記錄已完成')
    completeHomeVisitDialog.value = false
    await loadApplication()
    
    console.log('📋 Application after reload:', {
      home_visit_notes: application.value?.home_visit_notes,
      home_visit_document: application.value?.home_visit_document
    })
  } catch (err: any) {
    console.error('Failed to complete home visit:', err)
    notificationStore.error(err.response?.data?.detail || '完成家訪失敗')
  } finally {
    submitting.value = false
  }
}

// Request Documents
const requestDocuments = () => {
  requestDocumentsDialog.value = true
}

const confirmRequestDocuments = async () => {
  requestingDocuments.value = true
  try {
    await api.post(`/adoptions/applications/${application.value!.id}/request-documents`)
    
    requestDocumentsDialog.value = false
    notificationStore.success('已通知申請者補充文件')
    
    // Reload application to show updated status
    await loadApplication()
  } catch (err: any) {
    console.error('Failed to request documents:', err)
    notificationStore.error(err.response?.data?.detail || '通知補件失敗')
  } finally {
    requestingDocuments.value = false
  }
}

// Pet Unavailable Handling
const closePetUnavailableDialog = () => {
  petUnavailableDialog.value = false
  rejectionReason.value = ''
}

const rejectApplicationDueToPetUnavailable = async () => {
  if (!rejectionReason.value.trim()) {
    notificationStore.error('請輸入拒絕原因')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('rejection_reason', rejectionReason.value)

    await api.post(
      `/adoptions/applications/${application.value!.id}/reject-pet-unavailable`,
      formData
    )
    
    petUnavailableDialog.value = false
    rejectionReason.value = ''
    notificationStore.success('已通知申請者')
    
    // Reload application to show rejected status
    await loadApplication()
  } catch (err: any) {
    console.error('Failed to reject application:', err)
    notificationStore.error(err.response?.data?.detail || '拒絕申請失敗')
  } finally {
    submitting.value = false
  }
}

// Final Decision
const openFinalDecisionDialog = (approve: boolean) => {
  isApproving.value = approve
  finalDecisionNotes.value = ''
  finalDecisionDialog.value = true
}

const makeFinalDecision = async () => {
  if (!finalDecisionNotes.value) {
    notificationStore.error(isApproving.value ? '請填寫通過備註' : '請填寫拒絕原因')
    return
  }

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('decision', isApproving.value ? 'approved' : 'rejected')
    formData.append('notes', finalDecisionNotes.value)

    await api.post(
      `/adoptions/applications/${application.value!.id}/final-decision`,
      formData
    )
    
    notificationStore.success(isApproving.value ? '申請已通過' : '申請已拒絕')
    finalDecisionDialog.value = false
    loadApplication()
  } catch (err: any) {
    console.error('Failed to make final decision:', err)
    notificationStore.error(err.response?.data?.detail || '操作失敗')
  } finally {
    submitting.value = false
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'submitted':
    case 'document_review':
      return 'orange'
    case 'home_visit_scheduled':
      return 'blue'
    case 'home_visit_completed':
    case 'under_evaluation':
      return 'purple'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'error'
    default:
      return 'grey'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'submitted':
      return '已提交'
    case 'document_review':
      return '文件審核中'
    case 'home_visit_scheduled':
      return '家訪已安排'
    case 'home_visit_completed':
      return '家訪已完成'
    case 'under_evaluation':
      return '評估中'
    case 'approved':
      return '已通過'
    case 'rejected':
      return '已拒絕'
    default:
      return status
  }
}

const genderLabel = (gender: string | undefined) => {
  const labels: Record<string, string> = {
    male: '男生',
    female: '女生',
    unknown: '未知'
  }
  return gender ? (labels[gender] || gender) : '未知'
}

const sizeLabel = (size: string | undefined) => {
  const labels: Record<string, string> = {
    small: '小型',
    medium: '中型',
    large: '大型'
  }
  return size ? (labels[size] || size) : '未知'
}

const getPetStatusText = (status: string | undefined) => {
  const labels: Record<string, string> = {
    available: '可領養',
    pending: '審核中',
    adopted: '已被領養',
    unavailable: '不可領養'
  }
  return status ? (labels[status] || status) : '未知'
}

const housingTypeLabel = (type: string | undefined) => {
  const types: Record<string, string> = {
    apartment: '公寓',
    house: '獨棟住宅',
    rental: '租屋',
    owned: '自有'
  }
  return type ? (types[type] || type) : '-'
}

const getDocumentTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    // 英文值
    'identity': '身分證明',
    'residence': '居住證明',
    'income': '收入證明',
    'id_card': '身分證明',
    'residence_proof': '居住證明',
    'income_proof': '財力證明',
    'identity_proof': '身分證明',
    'address_proof': '地址證明',
    'financial_proof': '財力證明',
    // 中文值
    '身分證明': '身分證明',
    '居住證明': '居住證明',
    '收入證明': '收入證明',
    '財力證明': '財力證明',
    '地址證明': '地址證明'
  }
  return typeMap[type] || type
}

const formatIncome = (income: number | undefined) => {
  return income ? income.toLocaleString() : '-'
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const openImageViewer = (url: string) => {
  window.open(url, '_blank')
}

const isImageFile = (doc: any) => {
  if (doc.mime_type) {
    return doc.mime_type.startsWith('image/')
  }
  if (doc.file_name || doc.original_filename) {
    const filename = doc.original_filename || doc.file_name
    const ext = filename.toLowerCase().split('.').pop()
    return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(ext || '')
  }
  return false
}

const getDocumentUrl = (doc: any) => {
  return doc.file_url
}

const getPhotoUrl = (photo: any) => {
  return photo.file_url || photo.url
}
</script>

<style scoped>
.v-card-title {
  font-weight: 600;
}
</style>
