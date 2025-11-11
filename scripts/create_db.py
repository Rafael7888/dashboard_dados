import os
import sqlite3

# Garante que a pasta db/ existe
os.makedirs("db", exist_ok=True)

# Conectar/criar o ficheiro SQLite
conn = sqlite3.connect("db/app.db")
cur = conn.cursor()

# Ler o SQL do seed
with open("scripts/seed_sqlite.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

# Executar o script
cur.executescript(sql_script)

conn.commit()
conn.close()

print("Base de dados criada com sucesso em db/app.db")
