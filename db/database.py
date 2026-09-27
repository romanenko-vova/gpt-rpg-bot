import aiosqlite


async def create_database(app):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT UNIQUE,
            telegram_name TEXT
        )""")

        await db.execute("""CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT UNIQUE,
            name TEXT,
            race TEXT,
            class_name TEXT,
            description TEXT,
            backstory TEXT,
            portrait TEXT,
            stats TEXT,
            inventory TEXT,
            hp INTEGER,
            max_hp INTEGER
        )""")

        await db.execute("""CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT UNIQUE,
            history TEXT,
            last_scene TEXT,
            scene_image TEXT)""")
                        
        await db.commit()
