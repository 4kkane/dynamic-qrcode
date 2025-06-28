from flask import Flask, request, send_file, jsonify
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
    return jsonify(image_configs), 200

@app.route('/dcode/createqrcode', methods=['POST'])
def create_qrcode():
    data = request.json
    if not data or 'words' not in data:
        return jsonify({'error': 'Missing words in request body'}), 400

    words = data['words']
    # 可选参数
    version = data.get('version', 1)
    level = data.get('level', 'H')
    picture = data.get('picture')
    colorized = data.get('colorized', False)
    contrast = data.get('contrast', 1.0)
    brightness = data.get('brightness', 1.0)

    qrcode_id = str(uuid.uuid4())
    picture = "8820204ea82c4cf3bdc387acd4611d25.gif"
    # Determine output file extension based on picture extension
    output_extension = '.png' # Default to PNG
    if picture:
        # Extract extension from the picture filename
        _, ext = os.path.splitext(picture)
        if ext:
            output_extension = ext.lower()

    output_filename = f'{qrcode_id}{output_extension}'
    output_path = os.path.join('qrcodes', output_filename)

    # 确保qrcodes目录存在
    os.makedirs('qrcodes', exist_ok=True)

    # 处理图片路径
    actual_picture_path = None
    if picture:
        # 假设图片在项目的data目录下
        actual_picture_path = os.path.join(os.getcwd(), 'data', picture)
        if not os.path.exists(actual_picture_path):
            return jsonify({'error': f'Picture file not found: {actual_picture_path}'}), 400

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
        qrcodes[qrcode_id] = {
            'words': words,
            'version': version,
            'level': level,
            'picture': picture,
            'colorized': colorized,
            'contrast': contrast,
            'brightness': brightness,
            'filepath': output_path
        }
        return jsonify({'qrcode_id': qrcode_id, 'message': 'QR Code created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dcode/getqrcode/<qrcode_id>', methods=['GET'])
def get_qrcode(qrcode_id):
    qrcode_info = qrcodes.get(qrcode_id)
    if not qrcode_info:
        return jsonify({'error': 'QR Code not found'}), 404

    filepath = qrcode_info['filepath']
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    else:
        return jsonify({'error': 'QR Code file not found on server'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)