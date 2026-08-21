# CRUD — Create, Read, Update, Delete

import aiosqlite
import json

async def create_user(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
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
            user['stats'] = json.loads(user['stats'])
            return user
        return None
    
async def get_users():
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row # для возврата данных в виде словаря
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        return [dict(user) for user in users]
    
async def update_users_name(telegram_id: int, name: str):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("UPDATE users SET name = ? WHERE telegram_id = ?", (name, telegram_id))
        await db.commit()
        return await get_user_by_tg_id(telegram_id)
    
async def update_user(telegram_id: int, **kwargs):
    async with aiosqlite.connect("database.db") as db:
        for key, value in kwargs.items():
            # print(key, value)
            await db.execute(f"UPDATE users SET {key} = ? WHERE telegram_id = ?", (value, telegram_id))
        await db.commit()
        return await get_user_by_tg_id(telegram_id)
    
async def delete_user(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        await db.commit()
        return True