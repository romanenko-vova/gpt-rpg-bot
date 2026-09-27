import json

import aiosqlite


async def create_game(telegram_id: int, history: list[dict], last_scene: dict, scene_image: str):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO games (telegram_id, history, last_scene, scene_image) VALUES (?, ?, ?, ?)", 
            (telegram_id, json.dumps(history), json.dumps(last_scene), scene_image)
        )
        await db.commit()
        return await get_game_by_tg_id(telegram_id)

async def get_game_by_tg_id(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row 
        cursor = await db.execute("SELECT * FROM games WHERE telegram_id = ?", (telegram_id,))
        game = await cursor.fetchone()
        if game:
            game = dict(game)
            game['history'] = json.loads(game['history'])
            return game
        return None

async def update_game(telegram_id: int, **kwargs):
    async with aiosqlite.connect("database.db") as db:
        for key, value in kwargs.items():
            if key == "history":
                value = json.dumps(value)
            await db.execute(f"UPDATE games SET {key} = ? WHERE telegram_id = ?", (value, telegram_id))
        await db.commit()
        return await get_game_by_tg_id(telegram_id)

async def delete_game(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("DELETE FROM games WHERE telegram_id = ?", (telegram_id,))
        await db.commit()
        return True