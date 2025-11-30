<template>
  <div class="empty-favorites">
    <div class="empty-icon">
      <i class="mdi mdi-heart-outline"></i>
    </div>
    
    <h2 class="empty-title">還沒有收藏任何寵物</h2>
    
    <p class="empty-message">
      開始探索可愛的毛孩，找到您心儀的夥伴！<br>
      點擊 <i class="mdi mdi-heart"></i> 按鈕即可將寵物加入收藏清單。
    </p>

    <div class="empty-actions">
      <button @click="browsePets" class="btn btn-primary">
        <i class="mdi mdi-magnify"></i>
        瀏覽寵物
      </button>
    </div>

    <div class="empty-features">
      <div class="feature">
        <i class="mdi mdi-heart-multiple"></i>
        <h3>輕鬆管理收藏</h3>
        <p>將喜歡的寵物加入收藏，方便隨時查看</p>
      </div>
      <div class="feature">
        <i class="mdi mdi-bell"></i>
        <h3>即時更新</h3>
        <p>收藏寵物的狀態變化會即時通知您</p>
      </div>
      <div class="feature">
        <i class="mdi mdi-compare"></i>
        <h3>方便比較</h3>
        <p>收集多個候選寵物，輕鬆比較做出最佳選擇</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const browsePets = () => {
  router.push('/pets')
}
</script>

<style scoped>
.empty-favorites {
  max-width: 800px;
  margin: 0 auto;
  padding: 4rem 2rem;
  text-align: center;
}

/* Empty Icon */
.empty-icon {
  margin-bottom: 2rem;
}

.empty-icon .mdi {
  font-size: 8rem;
  color: #e0e0e0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}

/* Empty Title */
.empty-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
}

/* Empty Message */
.empty-message {
  font-size: 1.1rem;
  color: #7f8c8d;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.empty-message .mdi {
  color: #e91e63;
  vertical-align: middle;
  font-size: 1.3rem;
}

/* Empty Actions */
.empty-actions {
  margin-bottom: 4rem;
}

.btn {
  padding: 1rem 2.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(233, 30, 99, 0.4);
}

.btn-primary:active {
  transform: translateY(-1px);
}

.btn .mdi {
  font-size: 1.3rem;
}

/* Features */
.empty-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
  padding-top: 3rem;
  border-top: 2px solid #ecf0f1;
}

.feature {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.feature:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.feature .mdi {
  font-size: 3rem;
  color: #e91e63;
  margin-bottom: 1rem;
}

.feature h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.feature p {
  font-size: 0.95rem;
  color: #7f8c8d;
  line-height: 1.5;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .empty-favorites {
    padding: 2rem 1rem;
  }

  .empty-icon .mdi {
    font-size: 5rem;
  }

  .empty-title {
    font-size: 1.5rem;
  }

  .empty-message {
    font-size: 1rem;
  }

  .btn-primary {
    padding: 0.875rem 2rem;
    font-size: 1rem;
  }

  .empty-features {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .feature {
    padding: 1.25rem;
  }

  .feature .mdi {
    font-size: 2.5rem;
  }

  .feature h3 {
    font-size: 1.1rem;
  }

  .feature p {
    font-size: 0.9rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .empty-features {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
