from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
# DICA: No Render, altere essa chave para algo bem aleatório nas configurações de Environment Variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de Usuário com Hashing
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

# --- Rotas de Autenticação ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
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
            return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Rotas do Sistema ---

def carregar_catalogo():
    if os.path.exists('canais.json'):
        with open('canais.json', 'r', encoding='utf-8') as f:
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
