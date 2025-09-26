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

# Tratamento de erros para demonstrar CONFIABILIDADE
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Inicialização do banco de dados
def criar_tabelas():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        
        # Adicionar dados de exemplo se o banco estiver vazio
        if Livro.query.count() == 0:
            livros_exemplo = [
                Livro(titulo="Python para Iniciantes", autor="João Silva", 
                      isbn="9781234567890", ano_publicacao=2023, categoria="Programação",
                      quantidade_total=3, quantidade_disponivel=3),
                Livro(titulo="Algoritmos e Estruturas de Dados", autor="Maria Santos", 
                      isbn="9781234567891", ano_publicacao=2022, categoria="Programação",
                      quantidade_total=2, quantidade_disponivel=2),
                Livro(titulo="História do Brasil", autor="Pedro Oliveira", 
                      isbn="9781234567892", ano_publicacao=2021, categoria="História",
                      quantidade_total=1, quantidade_disponivel=1),
            ]
            
            usuarios_exemplo = [
                Usuario(nome="Ana Costa", email="ana@email.com", telefone="11999999999"),
                Usuario(nome="Carlos Lima", email="carlos@email.com", telefone="11888888888"),
            ]
            
            for livro in livros_exemplo:
                db.session.add(livro)
            
            for usuario in usuarios_exemplo:
                db.session.add(usuario)
            
            db.session.commit()
            logger.info("Dados de exemplo adicionados ao banco")

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True, host='0.0.0.0', port=5000)