import aiosqlite


async def register_user(telegram_id: int, telegram_name: str):
    # При первом /start добавляем игрока. Повторный /start не создаёт дубль.
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, telegram_name) VALUES (?, ?)",
            (telegram_id, telegram_name),
        )
        await db.commit()
