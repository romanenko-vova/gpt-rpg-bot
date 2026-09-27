import json

import aiosqlite


async def create_character(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO characters (telegram_id) VALUES (?)", (telegram_id,)
        )
        await db.commit()
        return await get_character_by_tg_id(telegram_id)

async def get_character_by_tg_id(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
            db.row_factory = aiosqlite.Row # для возврата данных в виде словаря
            cursor =await db.execute("SELECT * FROM characters WHERE telegram_id = ?", (telegram_id,))
            user = await cursor.fetchone()
            if user:
                user = dict(user)
                user['stats'] = json.loads(user['stats'])
                return user
            return None

async def update_character(telegram_id: int, **kwargs):
    async with aiosqlite.connect("database.db") as db:
        for key, value in kwargs.items():
            # print(key, value)
            await db.execute(f"UPDATE characters SET {key} = ? WHERE telegram_id = ?", (value, telegram_id))
        await db.commit()
        return await get_character_by_tg_id(telegram_id)