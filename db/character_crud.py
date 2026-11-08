import json

import aiosqlite


async def create_character(telegram_id: int):
    # Пустая карточка нужна, чтобы сохранять ответы игрока по одному.
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO characters (telegram_id) VALUES (?)",
            (telegram_id,),
        )
        await db.commit()


async def get_character(telegram_id: int):
    async with aiosqlite.connect("database.db") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM characters WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None

        # SQLite хранит характеристики как текст JSON. Бот работает со словарём.
        character = dict(row)
        if character["stats"]:
            character["stats"] = json.loads(character["stats"])
        return character


async def update_character(telegram_id: int, **fields):
    # На каждом шаге заполняем свои поля, например имя или портрет.
    async with aiosqlite.connect("database.db") as db:
        for column, value in fields.items():
            if column == "stats":
                value = json.dumps(value)
            await db.execute(
                f"UPDATE characters SET {column} = ? WHERE telegram_id = ?",
                (value, telegram_id),
            )
        await db.commit()
