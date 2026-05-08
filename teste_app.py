import pytest
from app import app, db, Livro, Usuario, validar_dados_livro

# ==========================================
# FIXTURES (Configuração do ambiente de teste)
# ==========================================

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all() 
            yield client   
            db.session.remove()
            db.drop_all() 

# ==========================================
# TESTES DE FUNÇÕES ISOLADAS (Unitários puros)
# ==========================================

def test_validar_dados_livro_com_sucesso():
    erros = validar_dados_livro(
        titulo="Senhor dos Anéis",
        autor="J.R.R. Tolkien",
        isbn="9780007136599",
        ano="1954",
        categoria="Fantasia"
    )
    assert len(erros) == 0 

def test_validar_dados_livro_com_erros():
    erros = validar_dados_livro("A", "B", "123", "abc", "C")
    
    assert len(erros) > 0
    assert "Título deve ter pelo menos 2 caracteres" in erros
    assert "Ano deve ser um número válido" in erros

# ==========================================
# TESTES DE ROTAS E BANCO DE DADOS (Integração)
# ==========================================

def test_pagina_inicial(client):
    resposta = client.get('/')
    assert resposta.status_code == 200
    assert b'html' in resposta.data.lower()

def test_adicionar_usuario(client):
    resposta = client.post('/usuarios/adicionar', data={
        'nome': 'Teste Silva',
        'email': 'teste@silva.com',
        'telefone': '11999999999'
    }, follow_redirects=True)
    
    assert resposta.status_code == 200
    
    usuario_no_banco = Usuario.query.filter_by(email='teste@silva.com').first()
    assert usuario_no_banco is not None
    assert usuario_no_banco.nome == 'Teste Silva'

def test_adicionar_usuario_sem_nome(client):
    resposta = client.post('/usuarios/adicionar', data={
        'nome': '', # Nome vazio!
        'email': 'vazio@silva.com',
        'telefone': '11999999999'
    }, follow_redirects=True)
    
    assert b'Nome deve ter pelo menos 2 caracteres' in resposta.data
    
    usuario_no_banco = Usuario.query.filter_by(email='vazio@silva.com').first()
    assert usuario_no_banco is None