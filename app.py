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


