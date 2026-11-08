import json

import aiosqlite

SCENES_PER_CHECKPOINT = 10


def read_saved_game(row):
    if row is None:
        return None

    # История и сцена лежат в SQLite как текст JSON.
    game = dict(row)
    game["history"] = json.loads(game["history"] or "[]")
    game["last_scene"] = json.loads(game["last_scene"] or "{}")
    return game


async def save_current_game(
    telegram_id: int,
    history: list[dict],
    last_scene: dict,
    scene_image: str,
    scene_count: int,
):
    # Коммит Артёма (52a6b6d): номер записывается вместе с историей и сценой.
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            """
            INSERT INTO games (telegram_id, history, last_scene, scene_image, scene_number)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                history = excluded.history,
                last_scene = excluded.last_scene,
                scene_image = excluded.scene_image,
                scene_number = excluded.scene_number
            """,
            (
                telegram_id,
                json.dumps(history),
                json.dumps(last_scene),
                scene_image,
                scene_count,
            ),
        )
        await db.commit()


async def get_current_game(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT *, scene_number AS scene_count FROM games WHERE telegram_id = ?",
            (telegram_id,),
        )
        return read_saved_game(await cursor.fetchone())


async def save_checkpoint(
    telegram_id: int,
    history: list[dict],
    last_scene: dict,
    scene_image: str,
    scene_count: int,
):
    # Сцена 10 попадает в первый слот, сцена 20 — во второй.
    slot = f"slot_{scene_count // SCENES_PER_CHECKPOINT}"
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            """
            INSERT INTO save_slots
                (telegram_id, save_slot, scene_count, history, last_scene, scene_image)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id, save_slot) DO UPDATE SET
                scene_count = excluded.scene_count,
                history = excluded.history,
                last_scene = excluded.last_scene,
                scene_image = excluded.scene_image
            """,
            (
                telegram_id,
                slot,
                scene_count,
                json.dumps(history),
                json.dumps(last_scene),
                scene_image,
            ),
        )
        await db.commit()


async def list_checkpoints(telegram_id: int):
    # Для меню нужны только номера слотов и сцен.
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT save_slot, scene_count FROM save_slots
            WHERE telegram_id = ? ORDER BY scene_count DESC
            """,
            (telegram_id,),
        )
        return await cursor.fetchall()


async def get_checkpoint(telegram_id: int, slot: str):
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM save_slots WHERE telegram_id = ? AND save_slot = ?",
            (telegram_id, slot),
        )
        return read_saved_game(await cursor.fetchone())
