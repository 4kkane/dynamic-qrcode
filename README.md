# 动态二维码生成器

这个项目使用Python和MyQR库来生成带有动态背景图的二维码，并提供了创建和查询接口。

## 功能

- 生成带有动态背景图的二维码
- 提供创建二维码的API接口
- 提供查询和获取二维码的API接口

## 安装

1. 克隆仓库
2. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

## 运行

```
python app.py
```

## 运行测试

确保 Flask 应用正在运行（通过 `python app.py` 启动）。

```bash
pytest test_app.py
```

## API 文档

### 创建二维码

`POST /create_qrcode`

请求体示例:
```json
{
    "words": "https://example.com",
    "picture": "background.gif",
    "colorized": true
}
```

### 获取二维码

`GET /get_qrcode/<qrcode_id>`

返回二维码图片文件

myqr.run() 参数说明：
```
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
```