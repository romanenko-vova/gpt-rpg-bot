import base64
import uuid
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

from config.config import IMAGE_MODEL_NAME, OPENROUTER_API_KEY, OR_BASE_URL

IMAGE_FOLDER = Path("images")


def image_to_data_url(image_path: str) -> str:
    # Для передачи портрета OpenRouter нужен текст с данными картинки.
    image_bytes = Path(image_path).read_bytes()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/png;base64,{encoded_image}"


async def generate_image(prompt: str, reference_image_path: str | None = None):
    request = {"model": IMAGE_MODEL_NAME, "prompt": prompt, "aspect_ratio": "1:1"}
    if reference_image_path:
        request["input_references"] = [
            {
                "type": "image_url",
                "image_url": {"url": image_to_data_url(reference_image_path)},
            }
        ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OR_BASE_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json=request,
        )
        response.raise_for_status()

    # Сервис присылает картинку текстом. Превращаем его в PNG на диске.
    encoded_image = response.json()["data"][0]["b64_json"]
    image_bytes = base64.b64decode(encoded_image)
    IMAGE_FOLDER.mkdir(exist_ok=True)
    image_path = IMAGE_FOLDER / f"{uuid.uuid4()}.png"
    with Image.open(BytesIO(image_bytes)) as image:
        image.save(image_path)

    return str(image_path)
