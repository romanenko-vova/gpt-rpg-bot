import base64
import uuid
from io import BytesIO

import httpx
from PIL import Image

from config.config import OPENROUTER_API_KEY, OR_BASE_URL


async def generate_image(prompt: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OR_BASE_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "sourceful/riverflow-v2.5-fast",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "modalities": ["image"],
            },
        )

        response.raise_for_status()
        data = response.json()
        print(data)
        # достаем url изображения
        image_url = data["choices"][0]["message"]["images"][0]["image_url"]["url"]
        print(image_url)
        # скачиваем изображение
        base64_str = image_url.split(",")[1]
        image_data = base64.b64decode(base64_str)
        # информация о картинке в байтах
        bytes_io = BytesIO(image_data)
        image = Image.open(bytes_io)
        path = f"images/{uuid.uuid4()}.png"
        image.save(path)
        return path
