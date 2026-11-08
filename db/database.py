import aiosqlite


async def create_database(_application):
    async with aiosqlite.connect("database.db") as db:
        # Игрок и его персонаж хранятся отдельно.
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
            portrait TEXT,
            stats TEXT,
            hp INTEGER,
            max_hp INTEGER
        )""")

        # Коммит Артёма (52a6b6d): сохраняем номер текущей сцены в SQLite.
        await db.execute("""CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT UNIQUE,
            history TEXT,
            last_scene TEXT,
            scene_image TEXT,
            scene_number INTEGER DEFAULT 1
        )""")

        # Старые записи без номера сцены загружаем по истории игры.
        cursor = await db.execute("PRAGMA table_info(games)")
        columns = [column[1] for column in await cursor.fetchall()]
        if "scene_number" not in columns:
            await db.execute("ALTER TABLE games ADD COLUMN scene_number INTEGER")

        # Коммиты Егора (e029782): контрольные точки хранятся отдельно.
        await db.execute("""CREATE TABLE IF NOT EXISTS save_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT,
            save_slot TEXT,
            scene_count INTEGER,
            history TEXT,
            last_scene TEXT,
            scene_image TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, save_slot)
        )""")

        await db.commit()
