from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import logging
from werkzeug.exceptions import BadRequest, InternalServerError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy(app)

class Livro(db.Model):
    """Modelo para representar um livro na biblioteca"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    ano_publicacao = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    quantidade_total = db.Column(db.Integer, default=1)
    quantidade_disponivel = db.Column(db.Integer, default=1)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True)
    
    def __repr__(self):
        return f'<Livro {self.titulo}>'

class Usuario(db.Model):
    """Modelo para representar um usuário da biblioteca"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    emprestimos = db.relationship('Emprestimo', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Emprestimo(db.Model):
    """Modelo para representar um empréstimo"""
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    data_emprestimo = db.Column(db.DateTime, default=datetime.utcnow)
    data_devolucao_prevista = db.Column(db.DateTime, nullable=False)
    data_devolucao_real = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ativo')  # ativo, devolvido, atrasado
    
    def __repr__(self):
        return f'<Emprestimo {self.id}>'

def validar_dados_livro(titulo, autor, isbn, ano, categoria):
    """
    Validação de dados para demonstrar CONFIABILIDADE
    """
    erros = []
    
    if not titulo or len(titulo.strip()) < 2:
        erros.append("Título deve ter pelo menos 2 caracteres")
    
    if not autor or len(autor.strip()) < 2:
        erros.append("Autor deve ter pelo menos 2 caracteres")
    
    if not isbn or len(isbn.strip()) < 10:
        erros.append("ISBN deve ter pelo menos 10 caracteres")
    
    try:
        ano_int = int(ano)
        if ano_int < 1000 or ano_int > datetime.now().year:
            erros.append("Ano de publicação inválido")
    except (ValueError, TypeError):
        erros.append("Ano deve ser um número válido")
    
    if not categoria or len(categoria.strip()) < 2:
        erros.append("Categoria deve ter pelo menos 2 caracteres")
    
    return erros

def calcular_estatisticas():
    """
    Cálculo de estatísticas para demonstrar EFICIÊNCIA
    """
    try:
        total_livros = Livro.query.count()
        total_usuarios = Usuario.query.count()
        emprestimos_ativos = Emprestimo.query.filter_by(status='ativo').count()
        emprestimos_atrasados = Emprestimo.query.filter(
            Emprestimo.data_devolucao_prevista < datetime.utcnow(),
            Emprestimo.status == 'ativo'
        ).count()
        
        return {
            'total_livros': total_livros,
            'total_usuarios': total_usuarios,
            'emprestimos_ativos': emprestimos_ativos,
            'emprestimos_atrasados': emprestimos_atrasados
        }
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {e}")
        return None
    
@app.route('/')
def index():
    """Página inicial demonstrando USABILIDADE"""
    try:
        estatisticas = calcular_estatisticas()
        livros_recentes = Livro.query.order_by(Livro.data_cadastro.desc()).limit(5).all()
        return render_template('index.html', 
                             estatisticas=estatisticas, 
                             livros_recentes=livros_recentes)
    except Exception as e:
        logger.error(f"Erro na página inicial: {e}")
        flash('Erro ao carregar dados da página inicial', 'error')
        return render_template('index.html', estatisticas=None, livros_recentes=[])