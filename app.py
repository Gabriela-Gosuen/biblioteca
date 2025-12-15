

from flask import Flask, render_template, request, redirect, url_for, flash,session
import sqlite3
import os
from waitress import serve

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"biblioteca.db")

def get_db_connection():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            livro_id INTEGER,
            data_emprestimo TEXT,
            data_devolucao TEXT,
            devolvido INTEGER DEFAULT 0,
            FOREIGN KEY(aluno_id) REFERENCES alunos(id),
            FOREIGN KEY(livro_id) REFERENCES livros(id)
        )
    ''')
   

init_db()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario=request.form['usuario']
        senha = request.form['senha']
        conn = get_db_connection()
        aluno = conn.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha)).fetchone()
        conn.close()
        if usuario:
            return redirect(url_for('dashboard'))
        else:
            flash('usuário ou senha incorretos!')
    return render_template('login.html')



@app.route('/cadastro_de_aluno', methods=['GET', 'POST'])
def cadastro_aluno():
    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO alunos (nome,matricula) VALUES (?, ?)', (nome,matricula))
            conn.commit()
            conn.close()
            flash('Aluno cadastrado com sucesso!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('aluno já cadastrado!')
    return render_template('cadastro_de_aluno.html')

@app.route('/cadastro_livros', methods=['GET', 'POST'])
def cadastro_livro():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano = request.form['ano']
        conn = get_db_connection()
        conn.execute('INSERT INTO livros (titulo, autor, ano) VALUES (?, ?, ?)', (titulo, autor, ano))
        conn.commit()
        conn.close()
        flash('Livro cadastrado com sucesso!')
    return render_template('cadastro_livros'
    '.html')

@app.route('/emprestimo', methods=['GET', 'POST'])
def emprestimo():
    conn = get_db_connection()
    alunos = conn.execute('SELECT * FROM alunos').fetchall()
    livros = conn.execute('SELECT * FROM livros').fetchall()
    if request.method == 'POST':
        aluno_id = request.form['aluno_id']
        livro_id = request.form['livro_id']
        data_emprestimo = request.form['data_emprestimo']
        conn.execute('INSERT INTO emprestimos (aluno_id, livro_id, data_emprestimo) VALUES (?, ?, ?)',
                     (aluno_id, livro_id, data_emprestimo))
        conn.commit()
        flash('Empréstimo registrado!')
    emprestimos = conn.execute('''
        SELECT e.id, a.nome, l.titulo, e.data_emprestimo, e.data_devolucao, e.devolvido
        FROM emprestimos e
        JOIN alunos a ON e.aluno_id = a.id
        JOIN livros l ON e.livro_id = l.id
    ''').fetchall()
    conn.close()
    return render_template('emprestimo.html', alunos=alunos, livros=livros, emprestimos=emprestimos)

@app.route('/devolucao/<int:id>', methods=['POST'])
def devolucao(id):
    data_devolucao = request.form['data_devolucao']
    conn = get_db_connection()
    conn.execute('UPDATE emprestimos SET devolvido = 1, data_devolucao = ? WHERE id = ?', (data_devolucao, id))
    conn.commit()
    conn.close()
    flash('Livro devolvido com sucesso!')
    return redirect(url_for('emprestimo'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
     port = int(os.environ.get("PORT",5000))
     app.run(host="0.0.0.0", port=port)
