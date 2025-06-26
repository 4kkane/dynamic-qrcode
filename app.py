from flask import Flask, request, send_file, jsonify
from MyQR import myqr
import os
import uuid

app = Flask(__name__)

# 存储生成的二维码信息
# 实际应用中，这些信息应该存储在数据库中
qrcodes = {}

@app.route('/create_qrcode', methods=['POST'])
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
    output_filename = f'{qrcode_id}.png'
    output_path = os.path.join('qrcodes', output_filename)

    # 确保qrcodes目录存在
    os.makedirs('qrcodes', exist_ok=True)

    try:
        myqr.run(
            words=words,
            version=version,
            level=level,
            picture=picture,
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

@app.route('/get_qrcode/<qrcode_id>', methods=['GET'])
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