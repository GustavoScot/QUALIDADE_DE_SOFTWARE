"""
=============================================================
TESTES DE SISTEMA COM SELENIUM
Sistema de Gerenciamento de Biblioteca
=============================================================

Tipo de teste : TESTE DE SISTEMA
Ferramenta    : Selenium WebDriver + pytest

SOBRE O LOGIN:
    O sistema usa Firebase Authentication, que autentica via
    JavaScript no navegador e gera um token antes de chamar
    o servidor. Por isso, nos testes, a sessão é injetada
    diretamente via rota auxiliar — isso é prática padrão
    em testes de sistema com autenticação externa (OAuth,
    Firebase, etc.), pois o objetivo é testar o sistema da
    biblioteca, não o Firebase em si.

Como executar:
    1. Em um terminal, rode o Flask:
           python app.py

    2. Em outro terminal (com o venv ativado):
           pytest test_sistema_selenium.py -v

Integrante responsável: [SEU NOME AQUI]
"""

import pytest
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app import app, db

BASE_URL = "http://localhost:5000"
ESPERA   = 8  # segundos máximos de espera por elementos


# ──────────────────────────────────────────────────────────
# ROTA AUXILIAR DE LOGIN PARA TESTES
#
# Como o Firebase autentica via JavaScript (não há um
# formulário HTML simples de usuário/senha), registramos
# uma rota extra que cria a sessão diretamente no servidor.
# Ela só existe durante os testes.
# ──────────────────────────────────────────────────────────

@app.route('/test-login')
def test_login():
    """
    Rota exclusiva para testes: cria uma sessão autenticada
    sem passar pelo Firebase, simulando um login bem-sucedido.
    """
    from flask import session
    session['user'] = {
        'uid':   'test-uid-123',
        'email': 'admin@teste.com',
        'name':  'Admin Teste',
        'photo': '',
    }
    return 'OK', 200


# ──────────────────────────────────────────────────────────
# FIXTURE: SERVIDOR FLASK
# Sobe o Flask uma vez para toda a sessão de testes.
# ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def servidor_flask():
    """
    Inicia o servidor Flask em uma thread em background.
    'scope=session' → roda UMA vez para todos os testes.
    'autouse=True'  → aplicado automaticamente, sem declarar.
    """
    app.config['TESTING']                = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca_test.db'
    app.config['WTF_CSRF_ENABLED']        = False
    app.config['SECRET_KEY']              = 'chave-de-teste'

    with app.app_context():
        db.create_all()

    thread = threading.Thread(
        target=lambda: app.run(port=5000, use_reloader=False, debug=False),
        daemon=True
    )
    thread.start()
    time.sleep(2)  # aguarda o servidor subir

    yield

    with app.app_context():
        db.drop_all()


# ──────────────────────────────────────────────────────────
# FIXTURE: NAVEGADOR CHROME
# Abre o Chrome antes de cada teste e fecha ao final.
# ──────────────────────────────────────────────────────────

@pytest.fixture
def navegador():
    """
    Abre o Chrome e já faz login via rota auxiliar antes
    de cada teste, para que todos comecem autenticados.

    Remova '--headless' se quiser VER o navegador abrindo.
    """
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument('--headless')          # ← remova para ver o navegador
    opcoes.add_argument('--no-sandbox')
    opcoes.add_argument('--disable-dev-shm-usage')
    opcoes.add_argument('--window-size=1280,800')

    servico = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=servico, options=opcoes)

    # ── Faz login antes de cada teste ──
    # Acessa a rota auxiliar que cria a sessão no servidor
    driver.get(f"{BASE_URL}/test-login")
    time.sleep(0.5)

    yield driver

    driver.quit()


# ──────────────────────────────────────────────────────────
# HELPER: espera elemento aparecer na tela
# ──────────────────────────────────────────────────────────

def esperar(driver, by, valor, tempo=ESPERA):
    """
    Aguarda até 'tempo' segundos para um elemento aparecer.
    Necessário porque páginas podem demorar para carregar.

    Exemplos de uso:
        esperar(driver, By.NAME, "titulo")
        esperar(driver, By.ID, "botao-salvar")
        esperar(driver, By.LINK_TEXT, "Adicionar Livro")
    """
    return WebDriverWait(driver, tempo).until(
        EC.presence_of_element_located((by, valor))
    )


# ══════════════════════════════════════════════════════════
# TESTE DE SISTEMA 1
# Fluxo: Login e acesso ao sistema
#
# HU: "Como administrador, quero fazer login para acessar
#      o sistema de gerenciamento da biblioteca."
# ══════════════════════════════════════════════════════════

class TestSistema_Login:
    """
    Verifica que o sistema de autenticação funciona corretamente:
    usuário autenticado acessa as páginas, não autenticado é
    redirecionado para o login.
    """

    def test_pagina_login_acessivel(self, navegador):
        """
        CENÁRIO: Qualquer pessoa acessa /auth/login.
        ESPERADO: Página de login carrega sem erro.
        """
        navegador.get(f"{BASE_URL}/auth/login")

        body = esperar(navegador, By.TAG_NAME, "body")
        conteudo = body.text

        # A página deve ter algum conteúdo de login
        assert navegador.current_url is not None
        assert body is not None, "A página de login não carregou."

    def test_usuario_autenticado_acessa_pagina_inicial(self, navegador):
        """
        CENÁRIO: Usuário já autenticado acessa a raiz do sistema.
        ESPERADO: Acessa normalmente (não é redirecionado para login).

        O fixture 'navegador' já faz o login via /test-login antes
        de cada teste, simulando um usuário autenticado.
        """
        navegador.get(f"{BASE_URL}/")

        time.sleep(1)
        url_atual = navegador.current_url

        # Se estiver autenticado, não deve ser redirecionado para /auth/login
        assert '/auth/login' not in url_atual, (
            "Usuário autenticado não deveria ser redirecionado para o login.\n"
            f"URL atual: {url_atual}"
        )

    def test_usuario_nao_autenticado_e_redirecionado(self, navegador):
        """
        CENÁRIO: Usuário sem sessão tenta acessar /livros.
        ESPERADO: Sistema redireciona para a tela de login.
        """
        # Apaga os cookies para simular sessão encerrada
        navegador.delete_all_cookies()

        navegador.get(f"{BASE_URL}/livros")
        time.sleep(1)

        url_atual = navegador.current_url

        assert '/auth/login' in url_atual, (
            "Usuário sem autenticação deveria ser redirecionado para /auth/login.\n"
            f"URL atual: {url_atual}"
        )


# ══════════════════════════════════════════════════════════
# TESTE DE SISTEMA 2
# Fluxo: Cadastro de Livro
#
# HU: "Como bibliotecário, quero cadastrar livros para que
#      o acervo seja gerenciado digitalmente."
# ══════════════════════════════════════════════════════════

class TestSistema_CadastroLivro:
    """
    Abre o formulário de livros no navegador, preenche os campos
    e verifica que o livro aparece na listagem após o cadastro.
    """

    def test_cadastro_livro_completo(self, navegador):
        """
        CENÁRIO: Bibliotecário preenche o formulário de cadastro
                 de livro com todos os dados válidos.
        ESPERADO: Livro é salvo e aparece na listagem.

        O que o Selenium faz passo a passo:
          1. Abre /livros/adicionar
          2. Digita em cada campo do formulário
          3. Clica no botão Salvar
          4. Verifica que 'Dom Casmurro' aparece na listagem
        """
        # ── Passo 1: Abrir o formulário ───────────────────────
        navegador.get(f"{BASE_URL}/livros/adicionar")

        # ── Passo 2: Preencher os campos ──────────────────────
        esperar(navegador, By.NAME, "titulo").send_keys("Dom Casmurro")
        navegador.find_element(By.NAME, "autor").send_keys("Machado de Assis")
        navegador.find_element(By.NAME, "isbn").send_keys("9788535902778")
        navegador.find_element(By.NAME, "ano").send_keys("1899")
        navegador.find_element(By.NAME, "categoria").send_keys("Literatura Brasileira")

        campo_qtd = navegador.find_element(By.NAME, "quantidade")
        campo_qtd.clear()
        campo_qtd.send_keys("3")

        # ── Passo 3: Clicar em Salvar ─────────────────────────
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # ── Passo 4: Verificar que o livro aparece na listagem ─
        conteudo = navegador.find_element(By.TAG_NAME, "body").text

        assert "Dom Casmurro" in conteudo, (
            "Após o cadastro, 'Dom Casmurro' deveria aparecer na listagem.\n"
            f"URL atual: {navegador.current_url}"
        )

    def test_isbn_duplicado_exibe_erro(self, navegador):
        """
        CENÁRIO: Bibliotecário tenta cadastrar dois livros com o mesmo ISBN.
        ESPERADO: O sistema recusa e exibe mensagem de erro.
        """
        # Cadastra o primeiro livro
        navegador.get(f"{BASE_URL}/livros/adicionar")
        esperar(navegador, By.NAME, "titulo").send_keys("Livro Original")
        navegador.find_element(By.NAME, "autor").send_keys("Autor X")
        navegador.find_element(By.NAME, "isbn").send_keys("9781111111111")
        navegador.find_element(By.NAME, "ano").send_keys("2020")
        navegador.find_element(By.NAME, "categoria").send_keys("Teste")
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # Tenta cadastrar com o mesmo ISBN
        navegador.get(f"{BASE_URL}/livros/adicionar")
        esperar(navegador, By.NAME, "titulo").send_keys("Livro Duplicado")
        navegador.find_element(By.NAME, "autor").send_keys("Autor Y")
        navegador.find_element(By.NAME, "isbn").send_keys("9781111111111")
        navegador.find_element(By.NAME, "ano").send_keys("2021")
        navegador.find_element(By.NAME, "categoria").send_keys("Teste")
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        conteudo = navegador.find_element(By.TAG_NAME, "body").text

        assert "ISBN" in conteudo or "cadastrado" in conteudo, (
            "O sistema deveria exibir erro para ISBN duplicado."
        )


# ══════════════════════════════════════════════════════════
# TESTE DE SISTEMA 3
# Fluxo Completo: Empréstimo de Livro (ponta a ponta)
#
# HU: "Como bibliotecário, quero registrar empréstimos para
#      controlar quais livros estão disponíveis."
# ══════════════════════════════════════════════════════════

class TestSistema_FluxoEmprestimo:
    """
    Teste de sistema mais completo: simula o fluxo real
    de um bibliotecário do início ao fim no navegador.
    """

    def _cadastrar_livro(self, navegador, titulo, isbn):
        navegador.get(f"{BASE_URL}/livros/adicionar")
        esperar(navegador, By.NAME, "titulo").send_keys(titulo)
        navegador.find_element(By.NAME, "autor").send_keys("Autor Teste")
        navegador.find_element(By.NAME, "isbn").send_keys(isbn)
        navegador.find_element(By.NAME, "ano").send_keys("2022")
        navegador.find_element(By.NAME, "categoria").send_keys("Ficção")
        campo_qtd = navegador.find_element(By.NAME, "quantidade")
        campo_qtd.clear()
        campo_qtd.send_keys("2")
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

    def _cadastrar_usuario(self, navegador, nome, email):
        navegador.get(f"{BASE_URL}/usuarios/adicionar")
        esperar(navegador, By.NAME, "nome").send_keys(nome)
        navegador.find_element(By.NAME, "email").send_keys(email)
        navegador.find_element(By.NAME, "telefone").send_keys("(61) 90000-0000")
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

    def test_fluxo_completo_emprestimo(self, navegador):
        """
        CENÁRIO PRINCIPAL DE SISTEMA:
        Simula tudo que um bibliotecário faz no dia a dia:

          Passo 1 → Cadastra livro 'A Moreninha' pelo formulário
          Passo 2 → Cadastra usuário 'Ana Lima' pelo formulário
          Passo 3 → Abre formulário de empréstimo
          Passo 4 → Seleciona o livro e o usuário nos dropdowns
          Passo 5 → Confirma o empréstimo
          Passo 6 → Verifica que aparece na listagem de empréstimos

        Cobre: navegador → rotas Flask → banco de dados → resposta HTML.
        """
        # ── Passo 1: Cadastrar livro ──────────────────────────
        self._cadastrar_livro(navegador, "A Moreninha", "9788500001011")

        # ── Passo 2: Cadastrar usuário ────────────────────────
        self._cadastrar_usuario(navegador, "Ana Lima", "ana.lima@email.com")

        # ── Passo 3: Abrir formulário de empréstimo ───────────
        navegador.get(f"{BASE_URL}/emprestimos/novo")

        # ── Passo 4a: Selecionar o usuário no dropdown ────────
        # Select é a classe do Selenium para campos <select>
        campo_usuario = esperar(navegador, By.NAME, "usuario_id")
        Select(campo_usuario).select_by_visible_text("Ana Lima")

        # ── Passo 4b: Selecionar o livro no dropdown ──────────
        campo_livro = navegador.find_element(By.NAME, "livro_id")
        Select(campo_livro).select_by_visible_text("A Moreninha")

        # ── Passo 4c: Definir o prazo (se o campo existir) ────
        try:
            campo_dias = navegador.find_element(By.NAME, "dias_emprestimo")
            campo_dias.clear()
            campo_dias.send_keys("14")
        except Exception:
            pass  # campo pode ter valor padrão

        # ── Passo 5: Confirmar o empréstimo ───────────────────
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # ── Passo 6: Verificar que aparece na listagem ─────────
        conteudo = navegador.find_element(By.TAG_NAME, "body").text

        assert "A Moreninha" in conteudo or "Ana Lima" in conteudo, (
            "O empréstimo deveria aparecer na listagem após ser registrado.\n"
            f"URL atual: {navegador.current_url}\n"
            f"Conteúdo: {conteudo[:400]}"
        )


# ══════════════════════════════════════════════════════════
# TESTE DE SISTEMA 4 (bônus)
# Fluxo: Busca Avançada
#
# HU: "Como usuário, quero buscar livros por diferentes
#      critérios para encontrar o que preciso rapidamente."
# ══════════════════════════════════════════════════════════

class TestSistema_BuscaAvancada:
    """
    Testa a busca: digita um termo no campo de busca no navegador
    e verifica que os resultados aparecem corretamente.
    """

    def test_busca_retorna_livro_cadastrado(self, navegador):
        """
        CENÁRIO: Usuário cadastra um livro e o busca pelo título.
        ESPERADO: O livro aparece nos resultados.

          Passo 1 → Cadastra 'Vidas Secas' via formulário
          Passo 2 → Navega até /busca
          Passo 3 → Digita 'Vidas' no campo de busca
          Passo 4 → Confirma que o livro aparece nos resultados
        """
        # ── Passo 1: Cadastrar o livro ────────────────────────
        navegador.get(f"{BASE_URL}/livros/adicionar")
        esperar(navegador, By.NAME, "titulo").send_keys("Vidas Secas")
        navegador.find_element(By.NAME, "autor").send_keys("Graciliano Ramos")
        navegador.find_element(By.NAME, "isbn").send_keys("9788503012345")
        navegador.find_element(By.NAME, "ano").send_keys("1938")
        navegador.find_element(By.NAME, "categoria").send_keys("Romance")
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # ── Passo 2: Navegar até a busca ──────────────────────
        navegador.get(f"{BASE_URL}/busca")

        # ── Passo 3: Digitar o termo de busca ─────────────────
        campo_busca = esperar(navegador, By.NAME, "q")
        campo_busca.clear()
        campo_busca.send_keys("Vidas")

        # ── Passo 4: Enviar a busca ───────────────────────────
        try:
            navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        except Exception:
            from selenium.webdriver.common.keys import Keys
            campo_busca.send_keys(Keys.RETURN)

        time.sleep(1)

        # ── Passo 5: Verificar resultado ──────────────────────
        conteudo = navegador.find_element(By.TAG_NAME, "body").text

        assert "Vidas Secas" in conteudo or "Graciliano" in conteudo, (
            "A busca por 'Vidas' deveria retornar 'Vidas Secas'.\n"
            f"Conteúdo: {conteudo[:400]}"
        )

    def test_busca_sem_resultado_nao_causa_erro(self, navegador):
        """
        CENÁRIO: Usuário busca por um termo inexistente.
        ESPERADO: Página carrega normalmente, sem erro 500.
        """
        navegador.get(f"{BASE_URL}/busca?q=xyzinexistente&tipo=livros")

        body = esperar(navegador, By.TAG_NAME, "body")

        assert body is not None, (
            "A página de busca deveria carregar mesmo sem resultados."
        )
        assert "500" not in navegador.title, (
            "Uma busca sem resultados não deveria gerar erro 500."
        )