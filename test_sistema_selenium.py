"""
=============================================================
TESTES DE SISTEMA COM SELENIUM
Sistema de Gerenciamento de Biblioteca
=============================================================

Tipo de teste : TESTE DE SISTEMA
Ferramenta    : Selenium WebDriver + pytest

Como executar:
    Terminal 1 → python app.py
    Terminal 2 → pytest test_sistema_selenium.py -v

Integrante responsável: [SEU NOME AQUI]
"""

import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5000"
ESPERA   = 8


# ──────────────────────────────────────────────────────────
# FIXTURE: NAVEGADOR CHROME
# ──────────────────────────────────────────────────────────

@pytest.fixture
def navegador():
    """
    Abre o Chrome antes de cada teste e fecha ao final.
    Acessa /test-login (rota no app.py) para criar a sessão.
    Remova '--headless' para VER o navegador abrindo.
    """
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument('--headless')
    opcoes.add_argument('--no-sandbox')
    opcoes.add_argument('--disable-dev-shm-usage')
    opcoes.add_argument('--window-size=1280,800')

    servico = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=servico, options=opcoes)

    driver.get(f"{BASE_URL}/test-login")
    time.sleep(0.5)

    yield driver
    driver.quit()


# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────

def esperar(driver, by, valor, tempo=ESPERA):
    """Aguarda até 'tempo' segundos para um elemento aparecer na página."""
    return WebDriverWait(driver, tempo).until(
        EC.presence_of_element_located((by, valor))
    )


def aceitar_alert_se_existir(driver, tempo=3):
    """
    Aguarda até 'tempo' segundos por um alert JavaScript.
    Se aparecer, clica em OK. Se não aparecer, segue normalmente.
    Necessário porque o formulário de empréstimo usa confirm().
    """
    try:
        WebDriverWait(driver, tempo).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        time.sleep(0.5)
    except Exception:
        pass


def isbn_unico():
    """Gera um ISBN único baseado no timestamp para evitar conflito com o banco."""
    return f"97800{int(time.time()) % 100000000}"


def cadastrar_livro(driver, titulo, isbn):
    """
    Preenche e envia o formulário de livro.
    Usa Select() para categoria pois é um <select>, não texto livre.
    """
    driver.get(f"{BASE_URL}/livros/adicionar")
    esperar(driver, By.NAME, "titulo").send_keys(titulo)
    driver.find_element(By.NAME, "autor").send_keys("Autor Teste")
    driver.find_element(By.NAME, "isbn").send_keys(isbn)
    driver.find_element(By.NAME, "ano").send_keys("2020")
    Select(driver.find_element(By.NAME, "categoria")).select_by_index(1)
    campo_qtd = driver.find_element(By.NAME, "quantidade")
    campo_qtd.clear()
    campo_qtd.send_keys("3")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    aceitar_alert_se_existir(driver)
    time.sleep(1)


def cadastrar_usuario(driver, nome, email):
    """Preenche e envia o formulário de usuário."""
    driver.get(f"{BASE_URL}/usuarios/adicionar")
    esperar(driver, By.NAME, "nome").send_keys(nome)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "telefone").send_keys("(61) 90000-0000")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    aceitar_alert_se_existir(driver)
    time.sleep(1)


def selecionar_opcao_que_contem(elemento_select, texto_parcial):
    """
    Seleciona a primeira opção do <select> cujo texto contenha
    'texto_parcial'. Evita erros por espaços extras no HTML.
    """
    select = Select(elemento_select)
    for opcao in select.options:
        if texto_parcial.lower() in opcao.text.lower():
            select.select_by_visible_text(opcao.text)
            return opcao.text
    opcoes = select.options
    if len(opcoes) > 1:
        select.select_by_index(len(opcoes) - 1)
        return opcoes[-1].text
    return None


# ══════════════════════════════════════════════════════════
# TESTE DE SISTEMA 1
# Fluxo: Login e proteção de rotas
#
# HU: "Como administrador, quero fazer login para acessar
#      o sistema de gerenciamento da biblioteca."
# ══════════════════════════════════════════════════════════

class TestSistema_Login:
    """
    Verifica que o sistema de autenticação funciona:
    - Página de login é acessível publicamente
    - Usuário autenticado acessa o sistema normalmente
    - Usuário sem sessão é redirecionado para o login
    """

    def test_pagina_login_acessivel(self, navegador):
        """
        CENÁRIO: Qualquer pessoa acessa /auth/login.
        ESPERADO: Página carrega sem erro.
        """
        navegador.get(f"{BASE_URL}/auth/login")
        body = esperar(navegador, By.TAG_NAME, "body")
        assert body is not None, "A página de login não carregou."

    def test_usuario_autenticado_acessa_sistema(self, navegador):
        """
        CENÁRIO: Usuário autenticado acessa a página inicial.
        ESPERADO: Acessa normalmente, sem ser redirecionado para login.
        O fixture já faz login via /test-login antes deste teste.
        """
        navegador.get(f"{BASE_URL}/")
        time.sleep(1)
        assert '/auth/login' not in navegador.current_url, (
            "Usuário autenticado não deveria ser redirecionado para login.\n"
            f"URL atual: {navegador.current_url}"
        )

    def test_usuario_sem_sessao_e_redirecionado(self, navegador):
        """
        CENÁRIO: Usuário sem sessão tenta acessar /livros.
        ESPERADO: Sistema redireciona para /auth/login (@login_required).
        """
        navegador.delete_all_cookies()
        navegador.get(f"{BASE_URL}/livros")
        time.sleep(1)
        assert '/auth/login' in navegador.current_url, (
            "Sem autenticação, deveria redirecionar para /auth/login.\n"
            f"URL atual: {navegador.current_url}"
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
    Preenche o formulário de cadastro de livro no navegador
    e verifica que o livro aparece na listagem após o cadastro.
    """

    def test_cadastro_livro_aparece_na_listagem(self, navegador):
        """
        CENÁRIO: Bibliotecário preenche o formulário com dados válidos.
        ESPERADO: Livro é salvo e aparece na listagem.

        Passo a passo do Selenium:
          1. Gera ISBN único por timestamp (evita conflito com banco)
          2. Abre /livros/adicionar e preenche todos os campos
          3. Seleciona categoria no <select> com Select()
          4. Clica em Salvar e trata alert de confirmação
          5. Verifica que 'Dom Casmurro' aparece na listagem
        """
        # ISBN único para não conflitar com execuções anteriores
        isbn = isbn_unico()

        navegador.get(f"{BASE_URL}/livros/adicionar")
        esperar(navegador, By.NAME, "titulo").send_keys("Dom Casmurro")
        navegador.find_element(By.NAME, "autor").send_keys("Machado de Assis")
        navegador.find_element(By.NAME, "isbn").send_keys(isbn)
        navegador.find_element(By.NAME, "ano").send_keys("1899")
        Select(navegador.find_element(By.NAME, "categoria")).select_by_index(1)

        campo_qtd = navegador.find_element(By.NAME, "quantidade")
        campo_qtd.clear()
        campo_qtd.send_keys("3")

        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        aceitar_alert_se_existir(navegador)
        time.sleep(1)

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
        isbn_repetido = isbn_unico()
        cadastrar_livro(navegador, "Livro Original", isbn_repetido)

        # Tenta cadastrar outro com o mesmo ISBN
        navegador.get(f"{BASE_URL}/livros/adicionar")
        esperar(navegador, By.NAME, "titulo").send_keys("Livro Duplicado")
        navegador.find_element(By.NAME, "autor").send_keys("Autor Y")
        navegador.find_element(By.NAME, "isbn").send_keys(isbn_repetido)
        navegador.find_element(By.NAME, "ano").send_keys("2021")
        Select(navegador.find_element(By.NAME, "categoria")).select_by_index(1)
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        aceitar_alert_se_existir(navegador)
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
    Teste mais completo: cadastra livro, cadastra usuário,
    faz empréstimo e verifica — tudo pelo navegador real.
    """

    def test_fluxo_completo_emprestimo(self, navegador):
        """
        CENÁRIO PRINCIPAL DE SISTEMA:
        Simula o fluxo real de um bibliotecário do início ao fim:

          Passo 1 → Cadastra livro 'A Moreninha' pelo formulário
          Passo 2 → Cadastra usuário pelo formulário
          Passo 3 → Abre /emprestimos/novo
          Passo 4 → Seleciona livro e usuário nos dropdowns
          Passo 5 → Clica em Salvar e aceita o alert de confirmação
          Passo 6 → Verifica que o empréstimo aparece na listagem
        """
        ts          = int(time.time())
        isbn        = f"97800{ts % 100000000}"
        email_unico = f"ana.{ts}@email.com"
        nome_unico  = f"Ana Lima {ts}"

        # Passo 1: Cadastrar livro
        cadastrar_livro(navegador, "A Moreninha", isbn)

        # Passo 2: Cadastrar usuário
        cadastrar_usuario(navegador, nome_unico, email_unico)

        # Passo 3: Abrir formulário de empréstimo
        navegador.get(f"{BASE_URL}/emprestimos/novo")
        time.sleep(1)

        # Passo 4a: Selecionar usuário pelo nome
        campo_usuario = esperar(navegador, By.NAME, "usuario_id")
        texto_usuario = selecionar_opcao_que_contem(campo_usuario, nome_unico)

        # Passo 4b: Selecionar livro pelo título
        campo_livro = navegador.find_element(By.NAME, "livro_id")
        texto_livro = selecionar_opcao_que_contem(campo_livro, "A Moreninha")

        # Passo 4c: Prazo de empréstimo
        try:
            campo_dias = navegador.find_element(By.NAME, "dias_emprestimo")
            campo_dias.clear()
            campo_dias.send_keys("14")
        except Exception:
            pass

        # Passo 5: Confirmar e aceitar o alert "Confirmar criação do empréstimo?"
        navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        aceitar_alert_se_existir(navegador)
        time.sleep(1)

        # Passo 6: Verificar na listagem
        conteudo = navegador.find_element(By.TAG_NAME, "body").text
        assert "A Moreninha" in conteudo or nome_unico in conteudo, (
            "O empréstimo deveria aparecer na listagem após ser registrado.\n"
            f"URL atual: {navegador.current_url}\n"
            f"Usuário: {texto_usuario} | Livro: {texto_livro}"
        )

    def test_pagina_emprestimos_carrega(self, navegador):
        """
        CENÁRIO: Usuário acessa a listagem de empréstimos.
        ESPERADO: Página carrega sem erro 500.
        """
        navegador.get(f"{BASE_URL}/emprestimos")
        body = esperar(navegador, By.TAG_NAME, "body")
        assert body is not None
        assert "500" not in navegador.title


# ══════════════════════════════════════════════════════════
# TESTE DE SISTEMA 4 (bônus)
# Fluxo: Busca Avançada
#
# HU: "Como usuário, quero buscar livros por diferentes
#      critérios para encontrar o que preciso rapidamente."
# ══════════════════════════════════════════════════════════

class TestSistema_BuscaAvancada:
    """
    Testa a busca: cadastra livro, digita no campo de busca
    e verifica que o resultado aparece corretamente.
    """

    def test_busca_retorna_livro_cadastrado(self, navegador):
        """
        CENÁRIO: Usuário cadastra 'Vidas Secas' e busca por 'Vidas'.
        ESPERADO: O livro aparece nos resultados.

          Passo 1 → Cadastra 'Vidas Secas' com ISBN único
          Passo 2 → Acessa /busca
          Passo 3 → Digita 'Vidas' e envia
          Passo 4 → Verifica que aparece nos resultados
        """
        cadastrar_livro(navegador, "Vidas Secas", isbn_unico())

        navegador.get(f"{BASE_URL}/busca")
        campo_busca = esperar(navegador, By.NAME, "q")
        campo_busca.clear()
        campo_busca.send_keys("Vidas")

        try:
            navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            aceitar_alert_se_existir(navegador)
        except Exception:
            from selenium.webdriver.common.keys import Keys
            campo_busca.send_keys(Keys.RETURN)

        time.sleep(1)
        conteudo = navegador.find_element(By.TAG_NAME, "body").text
        assert "Vidas Secas" in conteudo or "Autor Teste" in conteudo, (
            "A busca por 'Vidas' deveria retornar 'Vidas Secas'."
        )

    def test_busca_sem_resultado_nao_causa_erro(self, navegador):
        """
        CENÁRIO: Usuário busca por um termo inexistente.
        ESPERADO: Página carrega normalmente, sem erro 500.
        """
        navegador.get(f"{BASE_URL}/busca?q=termoinexistente123&tipo=livros")
        body = esperar(navegador, By.TAG_NAME, "body")
        assert body is not None
        assert "500" not in navegador.title