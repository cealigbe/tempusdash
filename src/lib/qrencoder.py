import segno, os, base64

from io import BytesIO
from PIL import Image

def encode_qr(data: str):
    qr = segno.make_qr(data, error="H")
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=20)
    buffer.seek(0)
    img = Image.open(buffer)
    return img

def encode_qr_base64(data: str):
    img = encode_qr(data)
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

if __name__ == "__main__":
    url = "https://chuck.aligbe.com"
    print(encode_qr_base64(url))
