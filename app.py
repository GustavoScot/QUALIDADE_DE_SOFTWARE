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
    
@app.route('/livros')
def listar_livros():
    """Lista todos os livros com funcionalidade de busca"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        busca = request.args.get('busca', '')
        categoria = request.args.get('categoria', '')
        
        query = Livro.query
        
        if busca:
            query = query.filter(
                db.or_(
                    Livro.titulo.contains(busca),
                    Livro.autor.contains(busca),
                    Livro.isbn.contains(busca)
                )
            )
        
        if categoria:
            query = query.filter(Livro.categoria == categoria)
        
        livros = query.paginate(
            page=pagina, per_page=10, error_out=False
        )
        
        categorias = db.session.query(Livro.categoria).distinct().all()
        categorias = [cat[0] for cat in categorias]
        
        return render_template('livros.html', 
                             livros=livros, 
                             categorias=categorias,
                             busca=busca,
                             categoria_selecionada=categoria)
    except Exception as e:
        logger.error(f"Erro ao listar livros: {e}")
        flash('Erro ao carregar lista de livros', 'error')
        return redirect(url_for('index'))

@app.route('/livros/adicionar', methods=['GET', 'POST'])
def adicionar_livro():
    """Adiciona um novo livro - FUNCIONALIDADE 1"""
    if request.method == 'POST':
        try:
            titulo = request.form['titulo'].strip()
            autor = request.form['autor'].strip()
            isbn = request.form['isbn'].strip()
            ano = request.form['ano']
            categoria = request.form['categoria'].strip()
            quantidade = int(request.form.get('quantidade', 1))
            
            erros = validar_dados_livro(titulo, autor, isbn, ano, categoria)
            
            if erros:
                for erro in erros:
                    flash(erro, 'error')
                return render_template('adicionar_livro.html')
            
            if Livro.query.filter_by(isbn=isbn).first():
                flash('ISBN já cadastrado no sistema', 'error')
                return render_template('adicionar_livro.html')
            
            novo_livro = Livro(
                titulo=titulo,
                autor=autor,
                isbn=isbn,
                ano_publicacao=int(ano),
                categoria=categoria,
                quantidade_total=quantidade,
                quantidade_disponivel=quantidade
            )
            
            db.session.add(novo_livro)
            db.session.commit()
            
            logger.info(f"Livro adicionado: {titulo} - {autor}")
            flash('Livro adicionado com sucesso!', 'success')
            return redirect(url_for('listar_livros'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao adicionar livro: {e}")
            flash('Erro ao adicionar livro', 'error')
            return render_template('adicionar_livro.html')
    
    return render_template('adicionar_livro.html')

@app.route('/usuarios')
def listar_usuarios():
    """Lista todos os usuários"""
    try:
        usuarios = Usuario.query.all()
        return render_template('usuarios.html', usuarios=usuarios)
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        flash('Erro ao carregar lista de usuários', 'error')
        return redirect(url_for('index'))

@app.route('/usuarios/adicionar', methods=['GET', 'POST'])
def adicionar_usuario():
    """Adiciona um novo usuário"""
    if request.method == 'POST':
        try:
            nome = request.form['nome'].strip()
            email = request.form['email'].strip()
            telefone = request.form.get('telefone', '').strip()
            
            if not nome or len(nome) < 2:
                flash('Nome deve ter pelo menos 2 caracteres', 'error')
                return render_template('adicionar_usuario.html')
            
            if not email or '@' not in email:
                flash('Email inválido', 'error')
                return render_template('adicionar_usuario.html')
            
            if Usuario.query.filter_by(email=email).first():
                flash('Email já cadastrado no sistema', 'error')
                return render_template('adicionar_usuario.html')
            
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                telefone=telefone
            )
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            logger.info(f"Usuário adicionado: {nome}")
            flash('Usuário adicionado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao adicionar usuário: {e}")
            flash('Erro ao adicionar usuário', 'error')
            return render_template('adicionar_usuario.html')
    
    return render_template('adicionar_usuario.html')

@app.route('/emprestimos')
def listar_emprestimos():
    """Lista todos os empréstimos - FUNCIONALIDADE 2"""
    try:
        status = request.args.get('status', 'todos')
        query = Emprestimo.query
        
        if status != 'todos':
            query = query.filter_by(status=status)
        
        emprestimos = query.order_by(Emprestimo.data_emprestimo.desc()).all()

        # Enriquecer dados para o template sem usar timedelta no Jinja
        agora_utc = datetime.utcnow()
        emprestimos_view = []
        total_ativos = 0
        total_devolvidos = 0
        total_atrasados = 0

        for emp in emprestimos:
            is_atrasado = (
                emp.status == 'ativo'
                and emp.data_devolucao_prevista is not None
                and emp.data_devolucao_prevista < agora_utc
            )
            if emp.status == 'ativo':
                total_ativos += 1
                if is_atrasado:
                    total_atrasados += 1
            elif emp.status == 'devolvido':
                total_devolvidos += 1

            emprestimos_view.append({
                'emprestimo': emp,
                'is_atrasado': is_atrasado,
            })

        stats = {
            'ativos': total_ativos,
            'devolvidos': total_devolvidos,
            'atrasados': total_atrasados,
            'total': len(emprestimos)
        }

        return render_template(
            'emprestimos.html',
            emprestimos=emprestimos_view,
            status_selecionado=status,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Erro ao listar empréstimos: {e}")
        flash('Erro ao carregar lista de empréstimos', 'error')
        return redirect(url_for('index'))

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
def novo_emprestimo():
    """Cria um novo empréstimo"""
    if request.method == 'POST':
        try:
            usuario_id = int(request.form['usuario_id'])
            livro_id = int(request.form['livro_id'])
            dias_emprestimo = int(request.form.get('dias_emprestimo', 14))
            
            # Verificar se livro está disponível
            livro = Livro.query.get(livro_id)
            if not livro or livro.quantidade_disponivel <= 0:
                flash('Livro não disponível para empréstimo', 'error')
                return redirect(url_for('novo_emprestimo'))
            
            # Verificar se usuário existe
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                flash('Usuário não encontrado', 'error')
                return redirect(url_for('novo_emprestimo'))
            
            # Criar empréstimo
            data_devolucao = datetime.utcnow() + timedelta(days=dias_emprestimo)
            novo_emprestimo = Emprestimo(
                usuario_id=usuario_id,
                livro_id=livro_id,
                data_devolucao_prevista=data_devolucao
            )
            
            # Atualizar quantidade disponível
            livro.quantidade_disponivel -= 1
            
            db.session.add(novo_emprestimo)
            db.session.commit()
            
            logger.info(f"Empréstimo criado: {livro.titulo} para {usuario.nome}")
            flash('Empréstimo realizado com sucesso!', 'success')
            return redirect(url_for('listar_emprestimos'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar empréstimo: {e}")
            flash('Erro ao criar empréstimo', 'error')
            return redirect(url_for('novo_emprestimo'))
    
    usuarios = Usuario.query.all()
    livros_disponiveis = Livro.query.filter(Livro.quantidade_disponivel > 0).all()
    return render_template('novo_emprestimo.html', usuarios=usuarios, livros=livros_disponiveis)

@app.route('/emprestimos/<int:emprestimo_id>/devolver', methods=['POST'])

def devolver_livro(emprestimo_id):
    """Devolve um livro emprestado"""
    try:
        emprestimo = Emprestimo.query.get_or_404(emprestimo_id)
        
        if emprestimo.status != 'ativo':
            flash('Empréstimo já foi devolvido', 'error')
            return redirect(url_for('listar_emprestimos'))
        
        # Atualizar empréstimo
        emprestimo.status = 'devolvido'
        emprestimo.data_devolucao_real = datetime.utcnow()
        
        # Atualizar quantidade disponível do livro
        emprestimo.livro.quantidade_disponivel += 1
        
        db.session.commit()
        
        logger.info(f"Livro devolvido: {emprestimo.livro.titulo}")
        flash('Livro devolvido com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao devolver livro: {e}")
        flash('Erro ao devolver livro', 'error')
    
    return redirect(url_for('listar_emprestimos'))


@app.route('/relatorios')
def relatorios():
    """Página de relatórios - FUNCIONALIDADE 3"""
    try:
        estatisticas = calcular_estatisticas()
        
        livros_populares_rows = db.session.query(
            Livro.titulo,
            Livro.autor,
            Livro.quantidade_disponivel,
            db.func.count(Emprestimo.id).label('total_emprestimos')
        ).join(Emprestimo).group_by(Livro.id).order_by(
            db.func.count(Emprestimo.id).desc()
        ).limit(10).all()

        livros_populares = [
            {
                'titulo': row.titulo,
                'autor': row.autor,
                'total_emprestimos': row.total_emprestimos,
                'disponivel': (row.quantidade_disponivel or 0) > 0,
            }
            for row in livros_populares_rows
        ]

        emprestimos_mensais = db.session.query(
            db.func.strftime('%Y-%m', Emprestimo.data_emprestimo).label('mes'),
            db.func.count(Emprestimo.id).label('total')
        ).filter(
            Emprestimo.data_emprestimo >= datetime.utcnow() - timedelta(days=180)
        ).group_by('mes').order_by('mes').all()
        
        return render_template(
            'relatorios.html',
            estatisticas=estatisticas,
            livros_populares=livros_populares,
            emprestimos_mensais=emprestimos_mensais
        )
    except Exception as e:
        logger.error(f"Erro ao gerar relatórios: {e}")
        flash('Erro ao gerar relatórios', 'error')
        return redirect(url_for('index'))
@app.route('/busca')
def busca_avancada():
    """BUSCA AVANÇADA"""
    try:
        termo = request.args.get('q', '').strip()
        tipo = request.args.get('tipo', 'todos')
        categoria = request.args.get('categoria', '')
        ano_min = request.args.get('ano_min','')
        ano_max = request.args.get('ano_max','')


        resultados = []


        if termo:
            if tipo == 'livros' or tipo == 'todos':
                query = Livro.query

                if termo:
                    query = query.filter(
                        db.or_(
                            Livro.titulo.contains(termo),
                            Livro.autor.contains(termo),
                            Livro.isbn.contains(termo)
                        )
                    )

                if categoria:
                    query = query.filter(Livro.categoria == categoria)

                if ano_min:
                    query = query.filter(Livro.ano_publicacao >= int(ano_min))

                if ano_max:
                    query = query.filter(Livro.ano_publicacao <= int(ano_max))
                
                livros = query.all()
                resultados.extend([('livro', livro) for livro in livros])

            if tipo == 'usuarios' or tipo == 'todos':
                usuarios = Usuario.query.filter(
                    db.or_(
                            Usuario.nome.contains(termo),
                            Usuario.email.contains(termo)
                    )
                ).all()
                resultados.extend([('usuario', usuario) for usuario in usuarios])

        categorias = db.session.query(Livro.categoria).distinct().all()
        categorias = [cat[0] for cat in categorias]

        return render_template('busca.html',
                               resultados = resultados,
                               categorias = categorias,
                               termo = termo,
                               tipo = tipo,
                               categoria = categoria,
                               ano_min = ano_min,
                               ano_max = ano_max)

    except Exception as e:
        logger.error(f"Erro na busca avançada: {e}")     
        flash('Erro na busca', 'error')
        return redirect(url_for('index'))







