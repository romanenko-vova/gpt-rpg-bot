import json

import aiosqlite


async def create_game(telegram_id: int, history: list[dict], last_scene: dict, scene_image: str):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            """
            INSERT INTO games (telegram_id, history, last_scene, scene_image)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                history = excluded.history,
                last_scene = excluded.last_scene,
                scene_image = excluded.scene_image
            """,
            (telegram_id, json.dumps(history), json.dumps(last_scene), scene_image),
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
            game["history"] = json.loads(game["history"]) if game.get("history") else []
            game["last_scene"] = json.loads(game["last_scene"]) if game.get("last_scene") else {}
            return game
        return None


async def update_game(telegram_id: int, **kwargs):
    async with aiosqlite.connect("database.db") as db:
        updates = {}

        if "history" in kwargs:
            updates["history"] = json.dumps(kwargs["history"])
        if "last_scene" in kwargs:
            updates["last_scene"] = json.dumps(kwargs["last_scene"])
        elif "last_scene_dic" in kwargs:
            updates["last_scene"] = json.dumps(kwargs["last_scene_dic"])
        if "scene_image" in kwargs:
            updates["scene_image"] = kwargs["scene_image"]
        elif "scene_image_path" in kwargs:
            updates["scene_image"] = kwargs["scene_image_path"]

        if not updates:
            return await get_game_by_tg_id(telegram_id)

        assignment_sql = ", ".join(f"{key} = ?" for key in updates)
        values = list(updates.values()) + [telegram_id]

        await db.execute(
            f"UPDATE games SET {assignment_sql} WHERE telegram_id = ?",
            tuple(values),
        )
        await db.commit()
        return await get_game_by_tg_id(telegram_id)


async def delete_game(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("DELETE FROM games WHERE telegram_id = ?", (telegram_id,))
        await db.commit()
        return True