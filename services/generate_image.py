import base64
import os
import uuid
from io import BytesIO

import httpx
from PIL import Image

from config.config import IMAGE_MODEL_NAME, OPENROUTER_API_KEY, OR_BASE_URL


async def generate_image(prompt: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OR_BASE_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": IMAGE_MODEL_NAME,
                "prompt": prompt
            },
        )

        response.raise_for_status()
        data = response.json()
        print(data)
        # достаем url изображения
        image_url = data['data'][0]["b64_json"]
        print(image_url)
        # скачиваем изображение
        image_data = base64.b64decode(image_url)
        # информация о картинке в байтах
        bytes_io = BytesIO(image_data)
        image = Image.open(bytes_io)
        if not os.path.exists("images"):
            os.makedirs("images")
        path = f"images/{uuid.uuid4()}.png"
        image.save(path)
        return path