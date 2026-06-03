import mysql.connector

def conectar():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="kemily123",
        database="sistema_escala"
    )
    return conexao