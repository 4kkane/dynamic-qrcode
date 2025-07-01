from flask import Flask, request, send_file, jsonify, send_from_directory
from MyQR import myqr
import os
import uuid
import yaml

app = Flask(__name__)

# 存储生成的二维码信息
# 实际应用中，这些信息应该存储在数据库中
qrcodes = {}

# 存储图片配置信息
image_configs = []

def _build_response(code, msg, body=None, status_code=200):
    if body is None:
        body = {}
    return jsonify({
        "ret": {
            "code": code,
            "msg": msg,
            "request_id": str(uuid.uuid4())
        },
        "body": body
    }), status_code

def load_image_configs():
    config_path = os.path.join(os.getcwd(), 'app.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config and 'images' in config:
                global image_configs
                image_configs = config['images']
                print(f"Loaded image configs: {image_configs}")
    else:
        print(f"Warning: app.yaml not found at {config_path}")

# 在应用启动时加载配置
load_image_configs()

@app.route('/dcode/list', methods=['GET'])
def list_images():
    return _build_response(0, "Success", {"images": image_configs})

@app.route('/dcode/createqrcode', methods=['POST'])
def create_qrcode():
    data = request.json
    if not data or 'words' not in data:
        return _build_response(400, "Missing required parameter: words", status_code=400)

    words = data['words']
    # 可选参数
    version = data.get('version', 1)
    level = data.get('level', 'H')
    picture = data.get('picture')
    colorized = data.get('colorized', False)
    contrast = data.get('contrast', 1.0)
    brightness = data.get('brightness', 0.5)

    qrcode_id = str(uuid.uuid4())
    # Determine output file extension based on picture extension
    output_extension = '.png' # Default to PNG
    actual_picture_path = None

    if picture:
        # Extract extension from the picture filename
        _, ext = os.path.splitext(picture)
        if ext:
            output_extension = ext.lower()
        # 假设图片在项目的data目录下
        actual_picture_path = os.path.join(os.getcwd(), 'data', picture)
        if not os.path.exists(actual_picture_path):
            return _build_response(400, f'Picture file not found: {actual_picture_path}')

    output_filename = f'{qrcode_id}{output_extension}'
    output_path = os.path.join('qrcodes', output_filename)

    # 确保qrcodes目录存在
    os.makedirs('qrcodes', exist_ok=True)

    try:
        myqr.run(
            words=words,
            version=version,
            level=level,
            picture=actual_picture_path, # 使用处理后的图片路径
            colorized=colorized,
            contrast=contrast,
            brightness=brightness,
            save_name=output_filename,
            save_dir='qrcodes'
        )
        qrcode_url = f'/qrcodes/{output_filename}'
        qrcodes[qrcode_id] = {
            'words': words,
            'version': version,
            'level': level,
            'picture': picture,
            'colorized': colorized,
            'contrast': contrast,
            'brightness': brightness,
            'filepath': output_path,
            'qrcode_url': qrcode_url
        }
        return _build_response(0, "QR Code created successfully", {"qrcode_id": qrcode_id, "qrcode_url": qrcode_url})
    except Exception as e:
        return _build_response(500, f"Error generating QR code: {str(e)}", status_code=500)

@app.route('/qrcodes/<filename>', methods=['GET'])
def get_qrcode(filename):
    try:
        qrcode_path = os.path.join('qrcodes', filename)
        if os.path.exists(qrcode_path):
            return send_file(qrcode_path, mimetype='image/png')
        else:
            return _build_response(404, "QR code not found", status_code=404)
    except Exception as e:
        return _build_response(500, f"Error retrieving QR code: {str(e)}", status_code=500)

@app.route('/dcode/getqrcode/<qrcode_id>', methods=['GET'])
def get_qrcode_by_id(qrcode_id):
    qrcode_info = qrcodes.get(qrcode_id)
    if not qrcode_info:
        return _build_response(404, "QR Code not found")

    filepath = qrcode_info.get('filepath')
    if filepath and os.path.exists(filepath):
        extension = qrcode_info.get('qrcode_url', '').split('.')[-1]
        return send_file(filepath, mimetype=f'image/{extension}')
    else:
        return _build_response(404, "QR Code image file not found on server")

@app.route('/data/<path:filename>')
def serve_data(filename):
    try:
        return send_from_directory('qrcodes', filename)
    except Exception as e:
        return _build_response(500, f"Error serving file: {str(e)}", status_code=500)

@app.route('/qrcodes/<path:filename>')
def serve_qrcode(filename):
    try:
        return send_from_directory('qrcodes', filename)
    except Exception as e:
        return _build_response(500, f"Error serving file: {str(e)}", status_code=500)

if __name__ == '__main__':
    app.run(debug=True, port=5000)