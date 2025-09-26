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






