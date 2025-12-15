import sqlite3

con = sqlite3.connect("biblioteca.db")
cur = con.cursor()

usuario = input("Digite o usuario: ")
senha = input("Digite a senha: ")

cur.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
con.commit()
con.close()

print("✅ Usuário criado com sucesso!")