# 动态二维码生成器

这个项目使用Python和MyQR库来生成带有动态背景图的二维码，并提供了创建和查询接口。

## 功能

- 生成带有动态背景图的二维码
- 提供创建二维码的API接口
- 提供查询和获取二维码的API接口
- 提供一个简单的H5页面用于生成和展示动态二维码

## 安装

1. 克隆仓库
2. 安装后端依赖:
   ```
   pip install -r server/requirements.txt
   ```
3. 安装前端依赖:
   ```bash
   cd web/vue_app
   npm install
   ```

## 运行

1. 启动后端服务:
   ```bash
   python server/app.py
   ```
2. 构建并启动前端服务:
   ```bash
   cd web/vue_app
   npm run build
   # 构建完成后，静态文件会生成在 web/dist 目录下
   # 你可以通过任何静态文件服务器（例如 Nginx, Apache, 或 Python 的 http.server）来部署 web/dist 目录
   ```

## 运行测试

确保 Flask 应用正在运行（通过 `python server/app.py` 启动）。

```bash
pytest server/test_app.py
```

## 访问 H5 页面

在完成前端构建后，通过浏览器访问 `web/dist/index.html` 文件即可。

## API 文档

### 配置

应用程序从 `server/app.yaml` 读取图片配置。`app.yaml` 示例：

```yaml
images:
  - id: "image1"
    name: "8820204ea82c4cf3bdc387acd4611d25.gif"
  - id: "image2"
    name: "another_image.png"
```

### 1. 列出可用图片

- **端点**: `/dqr/list`
- **方法**: `GET`
- **描述**: 从 `server/app.yaml` 中检索配置的图片 ID 和名称列表。
- **响应 (JSON)**:
  ```json
  {
    "ret": {
      "code": 0,
      "msg": "Success",
      "request_id": "string"
    },
    "body": {
      "images": [
        {
          "id": "image1",
          "name": "8820204ea82c4cf3bdc387acd4611d25.gif"
        },
        {
          "id": "image2",
          "name": "another_image.png"
        }
      ]
    }
  }
  ```

### 2. 创建二维码

- **端点**: `/create_qrcode`
- **方法**: `POST`
- **描述**: 生成带有可选背景图的动态二维码。
- **请求体 (JSON)**:
  ```json
  {
    "words": "您的二维码内容 (例如，URL 或文本)",
    "picture": "filename.gif",  // 可选: 背景图的文件名 (必须在项目根目录下的 'data' 文件夹中)
    "colorized": true,       // 可选: 是否对二维码进行着色 (默认: false)
    "contrast": 1.0,         // 可选: 背景图的对比度 (默认: 1.0)
    "brightness": 1.0        // 可选: 背景图的亮度 (默认: 1.0)
  }
  ```
- **请求示例 (cURL)**:
  ```bash
  curl --location --request POST 'http://127.0.0.1:5000/create_qrcode' \
  --header 'Content-Type: application/json' \
  --data-raw '{
      "words": "https://github.com/4kkane",
      "picture": "e51e4cdf847e4ee096585ff5a43a643f.gif",
      "colorized": true
  }'
  ```

![示例二维码](qrcodes/68317b54-4292-4b80-85c5-fb1ac73602d0.gif)

- **`picture` 参数说明**:
  - `picture` 参数应该是位于 `data` 文件夹中的图片文件名 (例如，`my_background.gif`)。
  - 如果背景图是 `.gif` 文件，生成的二维码也将是 `.gif` 文件。否则，它将是 `.png` 文件。
- **响应 (JSON)**:
  ```json
  {
    "ret": {
      "code": 0,
      "msg": "QR Code created successfully",
      "request_id": "string"
    },
    "body": {
      "qrcode_id": "生成的二维码的唯一ID",
      "qrcode_url": "/qrcodes/生成的二维码的唯一ID.png"
    }
  }
  ```



### 3. 获取二维码

- **端点**: `/get_qrcode/<qrcode_id>`
- **方法**: `GET`
- **描述**: 检索先前生成的二维码图片。
- **参数**:
  - `qrcode_id`: 要检索的二维码的唯一 ID。
- **响应**: 二维码图片 (PNG 或 GIF 格式)。

myqr.run() 参数说明：

**注意**：`data` 和 `qrcodes` 目录现在位于项目根目录下，而 `app.py` 位于 `server/` 目录下。


| 参数       | 描述                                       | 默认值                                                         |
| ---------- | ------------------------------------------ | -------------------------------------------------------------- |
| words      | 二维码的内容                               | 必填，无默认值                                                 |
| version    | 二维码的边长，单位非像素                   | 取决于你输入的信息的长度和使用的纠错等级                       |
| level      | 纠错水平，范围是L、M、Q、H，从左到右依次升高。 | H 纠错等级最高                                                 |
| picture    | 二维码的背景图片路径                       | None，不采用图片作为背景                                       |
| colorized  | 背景图片是否采用彩色                       | False，默认采用黑白图片                                        |
| contrast   | 调节图片的对比度                           | 1.0 表示原始图片，更小的值表示更低对比度，更大反之             |
| brightness | 调节图片的亮度                             | 1.0 表示原始图片，用法同 contrast                              |
| save_name  | 输出二维码文件名                           | "qrcode.png"                                                   |
| save_dir   | 输出目录                                   | 当前目录                                                       |
