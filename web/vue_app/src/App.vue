<template>
  <div id="app-container">
    <div class="header">
      <h1>动态二维码生成器</h1>
    </div>

    <div class="content">
      <div class="qrcode-display">
        <img v-if="qrcodeUrl" :src="qrcodeUrl" @error="handleImageError" alt="二维码" class="qrcode-image" />
        <div v-else class="placeholder">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-qr-code"><path d="M3 3h6v6H3z"></path><path d="M15 3h6v6h-6z"></path><path d="M3 15h6v6H3z"></path><path d="M15 15h6v6h-6z"></path><path d="M3 9h18"></path><path d="M9 3v18"></path></svg>
          <p>生成的二维码将显示在这里</p>
        </div>
      </div>

      <div class="form-controls">
        <div class="input-group">
          <input v-model="words" type="text" placeholder="请输入文本或URL" :disabled="isGenerating" />
        </div>

        <div class="input-group">
          <div class="select-container">
            <select v-model="selectedPicture" :disabled="isGenerating">
              <option value="" disabled>选择一个动图背景</option>
              <option v-for="image in gifImages" :key="image.id" :value="image.name">
                {{ image.name }}
              </option>
            </select>
            <span v-if="selectedPicture" class="clear-selection" @click="selectedPicture = ''">×</span>
          </div>
        </div>

        <button @click="generateQrCode" :disabled="isGenerating || !words || !selectedPicture" class="generate-button">
          <span v-if="isGenerating">
            <span class="spinner"></span>
            生成中...
          </span>
          <span v-else>生成二维码</span>
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="error-message" :class="{ 'retrying': errorMessage.includes('重试') }">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  setup() {
    const words = ref('');
    const gifImages = ref([]);
    const selectedPicture = ref('');
    const qrcodeUrl = ref('');
    const errorMessage = ref('');
    const isGenerating = ref(false);
    const timeoutIds = ref([]);

    const fetchGifImages = async () => {
      try {
        const response = await fetch('/dcode/list');
        const data = await response.json();
        if (data.ret.code === 0 && data.body && data.body.images) {
          gifImages.value = data.body.images.filter(image => image.name.endsWith('.gif'));
        } else {
          errorMessage.value = data.ret.msg || '获取图片列表失败。';
        }
      } catch (error) {
        errorMessage.value = '网络错误或服务器无响应。';
        console.error('Error fetching GIF images:', error);
      }
    };

    const clearAllTimeouts = () => {
      timeoutIds.value.forEach(id => clearTimeout(id));
      timeoutIds.value = [];
    };

    const createDelay = (ms) => {
      return new Promise((resolve) => {
        const id = setTimeout(resolve, ms);
        timeoutIds.value.push(id);
      });
    };

    const handleImageError = () => {
      if (qrcodeUrl.value) {
        errorMessage.value = '二维码图片加载失败，正在重试...';
        createDelay(1000).then(() => {
          const timestamp = new Date().getTime();
          qrcodeUrl.value = `${qrcodeUrl.value.split('?')[0]}?t=${timestamp}`;
        });
      } else {
        errorMessage.value = '二维码图片加载失败。';
      }
    };

    const checkImageUrl = async (url, retries = 3, delay = 1000) => {
      for (let i = 0; i < retries; i++) {
        try {
          const response = await fetch(url, { method: 'HEAD' });
          if (response.ok) {
            return true;
          }
          if (i < retries - 1) {
            await createDelay(delay);
          }
        } catch (error) {
          console.error(`Error checking image URL (attempt ${i + 1}/${retries}):`, error);
          if (i < retries - 1) {
            await createDelay(delay);
          }
        }
      }
      return false;
    };

    const generateQrCode = async () => {
      errorMessage.value = '';
      qrcodeUrl.value = '';
      isGenerating.value = true;

      if (!words.value.trim()) {
        errorMessage.value = '请输入URL或文本。';
        isGenerating.value = false;
        return;
      }

      try {
        const requestBody = {
          words: words.value.trim(),
          colorized: true,
        };
        if (selectedPicture.value) {
          requestBody.picture = selectedPicture.value;
        }

        const response = await fetch('/dcode/createqrcode', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
        });

        const data = await response.json();

        if (data.ret.code === 0 && data.body && data.body.qrcode_url) {
          const isImageAccessible = await checkImageUrl(data.body.qrcode_url, 3, 1000);
          if (isImageAccessible) {
            const timestamp = new Date().getTime();
            qrcodeUrl.value = `${data.body.qrcode_url}?t=${timestamp}`;
          } else {
            errorMessage.value = '二维码图片加载失败，请重新生成。';
          }
        } else {
          errorMessage.value = data.ret.msg || '生成二维码失败。';
        }
      } catch (error) {
        errorMessage.value = '网络错误或服务器无响应。';
        console.error('Error generating QR code:', error);
      } finally {
        isGenerating.value = false;
      }
    };

    onMounted(fetchGifImages);
    onUnmounted(clearAllTimeouts);

    return {
      words,
      gifImages,
      selectedPicture,
      qrcodeUrl,
      errorMessage,
      isGenerating,
      handleImageError,
      generateQrCode,
    };
  },
};
</script>

<style>
:root {
  --primary-color: #42b983;
  --background-color: #f0f2f5;
  --container-bg-color: #ffffff;
  --text-color: #333;
  --placeholder-color: #888;
  --border-color: #e0e0e0;
  --error-color: #ff4d4f;
  --warning-color: #faad14;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
}

#app-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.header {
  text-align: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 1.8rem;
  color: var(--primary-color);
  margin: 0;
}

.content {
  background-color: var(--container-bg-color);
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.qrcode-display {
  width: 100%;
  padding-top: 100%; /* 1:1 Aspect Ratio */
  position: relative;
  border-radius: 8px;
  background-color: #f9f9f9;
  border: 1px dashed var(--border-color);
  margin-bottom: 24px;
  overflow: hidden;
}

.qrcode-display .placeholder,
.qrcode-display .qrcode-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.qrcode-display .placeholder {
  color: var(--placeholder-color);
  text-align: center;
}

.placeholder .feather {
  color: #ccc;
  margin-bottom: 8px;
}

.qrcode-image {
  object-fit: contain;
}

.form-controls .input-group {
  margin-bottom: 16px;
}

.form-controls input,
.form-controls select {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-sizing: border-box;
  background-color: #fff;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-controls input:focus,
.form-controls select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

.select-container {
  position: relative;
}

.select-container select {
  appearance: none;
  -webkit-appearance: none;
  padding-right: 40px;
}

.select-container::after {
  content: '▼';
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  font-size: 12px;
  color: var(--placeholder-color);
  pointer-events: none;
}

.clear-selection {
  position: absolute;
  top: 50%;
  right: 35px;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 20px;
  color: #ccc;
  font-weight: bold;
}
.clear-selection:hover {
  color: #999;
}

.generate-button {
  width: 100%;
  padding: 14px;
  font-size: 1.1rem;
  font-weight: bold;
  color: #fff;
  background-color: var(--primary-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.generate-button:hover:not(:disabled) {
  background-color: #36a476;
}

.generate-button:active:not(:disabled) {
  transform: scale(0.98);
}

.generate-button:disabled {
  background-color: #a5d6c4;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  margin-top: 16px;
  padding: 10px;
  border-radius: 8px;
  color: #fff;
  background-color: var(--error-color);
}

.error-message.retrying {
  background-color: var(--warning-color);
}
</style>
