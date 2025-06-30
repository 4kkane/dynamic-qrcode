<template>
  <div id="app" class="container">
    <h1>动态二维码生成器</h1>

    <div class="form-group">
      <label for="url-input">输入URL或文本:</label>
      <input type="text" id="url-input" v-model="words" placeholder="例如: https://www.example.com">
    </div>

    <div class="form-group">
      <label for="picture-select">选择背景图片 (GIF):</label>
      <select id="picture-select" v-model="selectedPicture">
        <option value="">无背景图片</option>
        <option v-for="image in gifImages" :key="image.id" :value="image.name">{{ image.name }}</option>
      </select>
    </div>

    <button @click="generateQrCode">生成二维码</button>

    <div id="qrcode-display">
      <h2>生成的二维码:</h2>
      <img v-if="qrcodeUrl" :src="qrcodeUrl" alt="生成的二维码" class="qrcode-img">
      <p v-else class="qrcode-placeholder">二维码将显示在这里。</p>
    </div>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const words = ref('');
    const gifImages = ref([]);
    const selectedPicture = ref('');
    const qrcodeUrl = ref('');
    const errorMessage = ref('');

    // 获取 GIF 图片列表
    const fetchGifImages = async () => {
      try {
        const response = await fetch('/dqr/list');
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

    // 生成二维码
    const generateQrCode = async () => {
      errorMessage.value = '';
      qrcodeUrl.value = '';

      if (!words.value.trim()) {
        errorMessage.value = '请输入URL或文本。';
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

        const response = await fetch('/create_qrcode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (data.ret.code === 0 && data.body && data.body.qrcode_url) {
          qrcodeUrl.value = data.body.qrcode_url;
        } else {
          errorMessage.value = data.ret.msg || '生成二维码失败。';
        }
      } catch (error) {
        errorMessage.value = '网络错误或服务器无响应。';
        console.error('Error generating QR code:', error);
      }
    };

    onMounted(() => {
      fetchGifImages();
    });

    return {
      words,
      gifImages,
      selectedPicture,
      qrcodeUrl,
      errorMessage,
      generateQrCode
    };
  }
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
  background-color: #f4f4f4;
  color: #333;
}
.container {
  max-width: 600px;
  margin: 0 auto;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
h1 {
  text-align: center;
  color: #007bff;
  margin-bottom: 20px;
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
input[type="text"],
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
button:hover {
  background-color: #0056b3;
}
#qrcode-display {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
.qrcode-img {
  max-width: 100%;
  height: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
.qrcode-placeholder {
  color: #666;
}
.error-message {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>