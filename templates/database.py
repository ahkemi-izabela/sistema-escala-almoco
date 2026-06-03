import sqlite3

def conectar():
    conexao = sqlite3.connect("sistema_escala.db")
    conexao.row_factory = sqlite3.Row
    return conexao