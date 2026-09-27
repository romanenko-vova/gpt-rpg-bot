import json

import aiosqlite


async def create_user(telegram_id: int, telegram_name: str):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO users (telegram_id, telegram_name) VALUES (?, ?)", (telegram_id, telegram_name)
        )
        await db.commit()
        return await get_user_by_tg_id(telegram_id)

async def get_user_by_tg_id(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row # для возврата данных в виде словаря
        cursor =await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = await cursor.fetchone()
        if user:
            user = dict(user)
            if user and user.get('stats'):
                user['stats'] = json.loads(user['stats'])
            return user
        return None
    
async def get_users():
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row # для возврата данных в виде словаря
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        return [dict(user) for user in users]

async def delete_user(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        await db.commit()
        return True