import pytest
import pytest
import requests
import json
import os
import time
import shutil
from PIL import Image, ImageSequence

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Create a dummy PNG image for testing
    dummy_png_path = os.path.join(data_dir, 'test_image.png')
    if not os.path.exists(dummy_png_path):
        img = Image.new('RGB', (60, 30), color = 'red')
        img.save(dummy_png_path)

    # Create a dummy GIF image for testing
    dummy_gif_path = os.path.join(data_dir, 'test_image.gif')
    if not os.path.exists(dummy_gif_path):
        img = Image.new('RGB', (60, 30), color = 'blue')
        frames = []
        for i in range(5):
            new_frame = Image.new('RGB', (60, 30), color = (i*50, i*20, i*10))
            frames.append(new_frame)
        img.save(dummy_gif_path, save_all=True, append_images=frames, duration=100, loop=0)

    yield

    # Clean up generated QR codes and dummy images
    if os.path.exists('qrcodes'):
        shutil.rmtree('qrcodes')
        print("Cleaned up 'qrcodes' directory.")
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        print("Cleaned up 'data' directory.")

def test_list_images_success():
    url = f"{BASE_URL}/dqr/list"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Check if the dummy images from app.yaml are present
    assert any(img['id'] == 'image1' for img in response.json())
    assert any(img['name'] == '8820204ea82c4cf3bdc387acd4611d25.gif' for img in response.json())

def test_create_qrcode_success():
    url = f"{BASE_URL}/create_qrcode"
    headers = {'Content-Type': 'application/json'}
    data = {
        "words": "https://www.example.com",
        "picture": "test_image.png",
        "colorized": True,
        "contrast": 1.0,
        "brightness": 1.0
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert 'qrcode_id' in response.json()
    assert 'qrcode_url' in response.json()

def test_create_qrcode_missing_words():
    url = f"{BASE_URL}/create_qrcode"
    headers = {'Content-Type': 'application/json'}
    data = {
        "picture": "test_image.png"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert 'error' in response.json()
    assert response.json()['error'] == 'Missing required parameter: words'

def test_create_qrcode_invalid_picture():
    url = f"{BASE_URL}/create_qrcode"
    headers = {'Content-Type': 'application/json'}
    data = {
        "words": "https://www.example.com",
        "picture": "non_existent_image.png"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert 'error' in response.json()
    assert "Picture file not found" in response.json()['error']

def test_get_qrcode_success():
    # First, create a QR code to get an ID
    create_url = f"{BASE_URL}/create_qrcode"
    create_data = {
        "words": "https://www.example.com/get_test",
        "picture": "test_image.png"
    }
    create_response = requests.post(create_url, headers={'Content-Type': 'application/json'}, data=json.dumps(create_data))
    assert create_response.status_code == 200
    qrcode_id = create_response.json()['qrcode_id']

    # Then, try to retrieve it
    get_url = f"{BASE_URL}/get_qrcode/{qrcode_id}"
    get_response = requests.get(get_url)
    assert get_response.status_code == 200
    assert get_response.headers['Content-Type'] == 'image/png'

def test_get_qrcode_not_found():
    url = f"{BASE_URL}/get_qrcode/non_existent_id"
    response = requests.get(url)
    assert response.status_code == 404
    assert 'error' in response.json()
    assert response.json()['error'] == 'QR Code not found'

# Optional: Test with GIF image
def test_create_qrcode_gif_success():
    url = f"{BASE_URL}/create_qrcode"
    headers = {'Content-Type': 'application/json'}
    data = {
        "words": "https://www.example.com/gif_test",
        "picture": "test_image.gif",
        "colorized": True,
        "contrast": 1.0,
        "brightness": 1.0
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert 'qrcode_id' in response.json()
    assert 'qrcode_url' in response.json()
    assert response.json()['qrcode_url'].endswith('.gif')