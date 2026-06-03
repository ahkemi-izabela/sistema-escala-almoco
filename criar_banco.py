from database import conectar

conexao = conectar()
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    setor TEXT,
    cargo TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    horario_inicio TEXT NOT NULL,
    horario_fim TEXT NOT NULL,
    limite_funcionarios INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS escala_almoco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    horario_id INTEGER NOT NULL,
    data TEXT NOT NULL
)
""")

conexao.commit()

cursor.close()
conexao.close()

print("Banco SQLite criado com sucesso!")