import aiosqlite

async def create_database(app):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT UNIQUE,
            name TEXT NULL,
            class_name TEXT NULL,
            race TEXT NULL,
            description TEXT NULL,
            portrait TEXT NULL,
            stats TEXT NULL
        )""")
        await db.commit()

