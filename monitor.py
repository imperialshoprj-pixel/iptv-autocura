from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)

# Configurações de Segurança
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-super-secreta-altere-isso')

# CORREÇÃO PARA O RENDER: O banco deve estar em uma pasta persistente ou na raiz.
# Usamos o caminho absoluto baseado no diretório do arquivo.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'usuarios.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELO DO BANCO DE DADOS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos!', 'danger')
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe!', 'danger')
        else:
            novo_user = User(username=username)
            novo_user.set_password(password)
            db.session.add(novo_user)
            db.session.commit()
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROTAS DO SISTEMA ---

def carregar_catalogo():
    caminho_json = os.path.join(os.path.dirname(__file__), 'canais.json')
    if os.path.exists(caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/')
@login_required
def index():
    return render_template('index.html', catalogo=carregar_catalogo())

@app.route('/filme/<filme_id>')
@login_required
def filme(filme_id):
    catalogo = carregar_catalogo()
    filme_data = catalogo.get(filme_id)
    if not filme_data:
        abort(404)
    return render_template('player.html', filme=filme_data)

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    # O contexto do aplicativo garante que o banco seja criado corretamente
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
