
import os
from core.database import Base, engine


print("=== Инициализация базы данных ===")

delete_db = input("Удалить старую базу locals.db? (y/n): ").lower() == 'y'

if delete_db and os.path.exists("locals.db"):
    os.remove("locals.db")
    print("Старая база удалена")
else:
    print("Старая база сохранена (если была)")

print("Создаём/обновляем таблицы...")
Base.metadata.create_all(bind=engine)
print("Готово! Таблицы созданы/обновлены.")
print("Можно запускать сервер.")