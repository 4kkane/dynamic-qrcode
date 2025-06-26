import pytest
import requests
import os
import time

# 假设 Flask 应用运行在本地 5000 端口
BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="module")
def flask_app_url():
    # 启动 Flask 应用的命令，这里假设你已经手动启动了或者通过其他方式启动
    # 为了测试，我们假设应用已经运行
    # 如果需要自动启动，可以使用 subprocess 模块，但需要更复杂的清理逻辑
    print(f"\nAssuming Flask app is running at {BASE_URL}")
    yield BASE_URL

def test_create_qrcode_success(flask_app_url):
    url = f"{flask_app_url}/create_qrcode"
    payload = {
        "words": "https://github.com/4kkane",
        "picture": None, # 暂时不使用图片，避免测试环境依赖
        "colorized": False
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert 'qrcode_id' in data
    assert 'message' in data
    assert data['message'] == 'QR Code created successfully'
    print(f"Created QR Code ID: {data['qrcode_id']}")

    # 存储 qrcode_id 以便后续测试获取
    pytest.current_qrcode_id = data['qrcode_id']

def test_create_qrcode_missing_words(flask_app_url):
    url = f"{flask_app_url}/create_qrcode"
    payload = {
        "picture": None
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'Missing words in request body'

def test_get_qrcode_success(flask_app_url):
    # 确保 test_create_qrcode_success 已经运行并设置了 qrcode_id
    if not hasattr(pytest, 'current_qrcode_id'):
        pytest.fail("test_create_qrcode_success did not run or failed to set qrcode_id")

    qrcode_id = pytest.current_qrcode_id
    url = f"{flask_app_url}/get_qrcode/{qrcode_id}"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
    # 验证文件是否存在且非空
    assert len(response.content) > 0
    print(f"Successfully retrieved QR Code for ID: {qrcode_id}")

def test_get_qrcode_not_found(flask_app_url):
    url = f"{flask_app_url}/get_qrcode/non_existent_id"
    response = requests.get(url)
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'QR Code not found'

# 清理生成的二维码文件 (可选，根据需要决定是否在测试后删除)
@pytest.fixture(scope="module", autouse=True)
def cleanup_qrcodes():
    yield
    # 可以在这里添加清理逻辑，例如删除 'qrcodes' 目录下的文件
    # import shutil
    # if os.path.exists('qrcodes'):
    #     shutil.rmtree('qrcodes')
    #     print("Cleaned up 'qrcodes' directory.")