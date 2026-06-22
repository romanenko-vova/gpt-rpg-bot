import asyncio

from services.generate_text import generate_text

print(asyncio.run(generate_text("Привет, придумай мне имя для персонажа. Объясни почему именно оно")))