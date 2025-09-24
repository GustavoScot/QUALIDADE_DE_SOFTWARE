@app.route('/busca')
def busca_avancada():
    """BUSCA AVANÇADA"""
    try:
        termo = request.args.get('q', '').strip()
        tipo = request.args.get('tipo', 'todos')
        categoria = request.args.get('categoria', '')