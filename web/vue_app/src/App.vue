<template>
  <div class="container">
    <h1>动态二维码生成器</h1>
    <div class="form-group">
      <div class="input-row">
        <input
          v-model="words"
          type="text"
          placeholder="请输入文字内容"
          :disabled="isGenerating"
        />
        <select
          v-model="selectedPicture"
          :disabled="isGenerating"
        >
          <option value="">请选择动图</option>
          <option
            v-for="image in gifImages"
            :key="image.id"
            :value="image.name"
          >
            {{ image.name }}
          </option>
        </select>
      </div>
      <div class="button-group">
        <button
          @click="generateQrCode"
          :disabled="isGenerating || !words || !selectedPicture"
          class="generate-btn"
        >
          {{ isGenerating ? '生成中...' : '生成二维码' }}
        </button>
        <button
          @click="resetForm"
          :disabled="isGenerating || (!words && !selectedPicture && !qrcodeUrl)"
          class="reset-btn"
        >
          重置
        </button>
      </div>
    </div>
    <div class="qrcode-container">
      <img
        v-if="qrcodeUrl"
        :src="qrcodeUrl"
        @error="handleImageError"
        alt="二维码"
      />
      <div
        v-else
        class="placeholder"
      >
        二维码将显示在这里
      </div>
    </div>
    <div
      v-if="errorMessage"
      :class="['error-message', { 'retrying': errorMessage.includes('重试') }]"
    >
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

    // 获取 GIF 图片列表
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

    // 处理图片加载错误
    const handleImageError = () => {
      if (qrcodeUrl.value) {
        errorMessage.value = '二维码图片加载失败，正在重试...';
        // 延迟1秒后重试加载，添加时间戳避免缓存
        createDelay(1000).then(() => {
          const timestamp = new Date().getTime();
          qrcodeUrl.value = `${qrcodeUrl.value}?t=${timestamp}`;
        });
      } else {
        errorMessage.value = '二维码图片加载失败。';
      }
    };

    // 存储定时器ID
    const timeoutIds = ref([]);

    // 清理所有定时器
    const clearAllTimeouts = () => {
      timeoutIds.value.forEach(id => clearTimeout(id));
      timeoutIds.value = [];
    };

    // 创建可取消的延迟
    const createDelay = (ms) => {
      return new Promise((resolve) => {
        const id = setTimeout(resolve, ms);
        timeoutIds.value.push(id);
      });
    };

    // 检查图片URL是否可访问
    const checkImageUrl = async (url, retries = 3, delay = 1000) => {
      for (let i = 0; i < retries; i++) {
        try {
          const response = await fetch(url, { method: 'HEAD' });
          if (response.ok) {
            return true;
          }
          // 如果不是最后一次重试，则等待指定时间后继续
          if (i < retries - 1) {
            await createDelay(delay);
          }
        } catch (error) {
          console.error(`Error checking image URL (attempt ${i + 1}/${retries}):`, error);
          // 如果不是最后一次重试，则等待指定时间后继续
          if (i < retries - 1) {
            await createDelay(delay);
          }
        }
      }
      return false;
    };

    // 生成二维码
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
          colorized: true // 默认着色
        };
        if (selectedPicture.value) {
          requestBody.picture = selectedPicture.value;
        }

        const response = await fetch('/dcode/createqrcode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (data.ret.code === 0 && data.body && data.body.qrcode_url) {
          // 检查生成的二维码图片是否可访问（最多重试3次，每次间隔1秒）
          const isImageAccessible = await checkImageUrl(data.body.qrcode_url, 3, 1000);
          if (isImageAccessible) {
            // 添加时间戳避免缓存
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

    onMounted(() => {
      fetchGifImages();
    });

    onUnmounted(() => {
      clearAllTimeouts();
    });

    // 重置表单状态
    const resetForm = () => {
      words.value = '';
      selectedPicture.value = '';
      qrcodeUrl.value = '';
      errorMessage.value = '';
      isGenerating.value = false;
      clearAllTimeouts();
    };

    return {
      words,
      gifImages,
      selectedPicture,
      qrcodeUrl,
      errorMessage,
      generateQrCode,
      handleImageError,
      isGenerating,
      resetForm
    };
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.input-row {
  display: flex;
  gap: 10px;
}

input {
  flex: 2;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

select {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.button-group {
  display: flex;
  gap: 10px;
}

.generate-btn {
  flex: 2;
  padding: 12px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.reset-btn {
  flex: 1;
  padding: 12px 20px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.generate-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.reset-btn:hover:not(:disabled) {
  background-color: #f57c00;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.qrcode-container {
  width: 100%;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 2px dashed #ddd;
}

.qrcode-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.placeholder {
  color: #999;
  font-size: 16px;
}

.error-message {
  color: #ff4444;
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  padding: 10px;
  border-radius: 4px;
  background-color: #ffebee;
}

.error-message.retrying {
  color: #ff9800;
  background-color: #fff3e0;
}
</style>