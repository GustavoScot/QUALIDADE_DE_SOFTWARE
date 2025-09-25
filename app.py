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