
# 📚 Sistema de Gerenciamento de Biblioteca  

## 📝 Descrição do Projeto  
Este projeto é um **Sistema de Gerenciamento de Biblioteca** desenvolvido em **Python com Flask**.  
Ele foi pensado para demonstrar, na prática, as características da **ISO/IEC 25010** aplicadas à qualidade de software.  

O sistema traz funcionalidades completas para gerenciar livros, usuários, empréstimos e relatórios, com foco em **usabilidade, confiabilidade e funcionalidade**.  

---

## 🎯 Objetivos  
- Colocar em prática os conceitos da ISO/IEC 25010  
- Desenvolver uma aplicação web funcional, organizada e intuitiva  
- Utilizar boas práticas de programação e documentação  
- Criar uma interface moderna, responsiva e fácil de usar  

---

## 🚀 Funcionalidades  

### 📖 Cadastro de Livros  
- Cadastro completo com informações detalhadas  
- Validação de dados (ISBN único, campos obrigatórios)  
- Controle de exemplares e categorização por área de conhecimento  
- Interface simples e intuitiva  

### 🔄 Sistema de Empréstimos  
- Controle de empréstimos e devoluções  
- Gestão de prazos e status  
- Identificação de atrasos  
- Interface prática para criação e gestão de empréstimos  

### 📊 Relatórios e Estatísticas  
- Estatísticas gerais do sistema  
- Ranking dos livros mais emprestados  
- Análise por período  
- Visualização de dados de forma clara  

### 🔍 Busca Avançada  
- Busca por múltiplos critérios (título, autor, ISBN)  
- Filtros por categoria e período  
- Resultados organizados e de fácil leitura  

---

## 🏆 ISO/IEC 25010 na Prática  
- **Funcionalidade:** todas as funções implementadas, com CRUD completo, filtros e relatórios  
- **Confiabilidade:** tratamento de erros, logs, páginas personalizadas (404/500) e recuperação de falhas  
- **Usabilidade:** interface responsiva, design com Bootstrap, navegação intuitiva e validação em tempo real  

---

## 🛠️ Tecnologias Utilizadas  
- **Backend:** Python 3.x + Flask 2.3.3  
- **Banco de Dados:** SQLite + SQLAlchemy  
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.1.3  
- **Ícones:** Font Awesome 6.0.0  
- **Controle de Versão:** Git  

---

## 📋 Pré-requisitos  
- Python 3.7 ou superior  
- pip (gerenciador de pacotes)  
- Git  

---

## ⚙️ Como Executar  

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sistema-biblioteca.git
cd sistema-biblioteca

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app.py
````

Acesse no navegador: **[http://localhost:5000](http://localhost:5000)**

---

## 📁 Estrutura do Projeto

```
sistema-biblioteca/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências do projeto
├── README.md              # Documentação do projeto
├── biblioteca.db          # Banco de dados SQLite (criado automaticamente)
└── templates/             # Templates HTML
    ├── base.html
    ├── index.html
    ├── livros.html
    ├── adicionar_livro.html
    ├── usuarios.html
    ├── adicionar_usuario.html
    ├── emprestimos.html
    ├── novo_emprestimo.html
    ├── relatorios.html
    ├── busca.html
    ├── 404.html
    └── 500.html
```

---

## 🎮 Como Usar

1. **Cadastro de Livros** → Vá em *Livros → Adicionar Livro*
2. **Cadastro de Usuários** → Vá em *Usuários → Adicionar Usuário*
3. **Empréstimos** → Vá em *Empréstimos → Novo Empréstimo*
4. **Relatórios** → Vá em *Relatórios* e explore estatísticas
5. **Busca Avançada** → Use filtros e critérios para encontrar o que precisa

---

## 👥 Equipe de Desenvolvimento

* **Grazielly Sabino** → Desenvolvimento da funcionalidade de **Empréstimos de Livros** e revisão de pull requests
* **Gustavo Scot** → Organização das tarefas, desenvolvimento da funcionalidade de **Livros** e revisão de pull requests
* **Jeferson Lucas** → Desenvolvimento da **Busca Avançada**, revisão de pull requests e apoio na organização do projeto
* **Kaion B. Lima** → Desenvolvimento da funcionalidade de **Relatórios**, revisão de pull requests e responsável pela **documentação**

---

## 🔮 Melhorias Futuras

* Sistema de autenticação de usuários
* Notificações por e-mail
* API REST para integração
* Testes automatizados
* Deploy em produção
* Backup automático do banco de dados

---

## 📄 Licença

Projeto sob licença **MIT**. Consulte o arquivo LICENSE para mais detalhes.

---

## 📞 Contato

Dúvidas ou sugestões? Entre em contato pelos canais disponíveis no repositório.

Desenvolvido com ❤️ pela equipe para demonstrar qualidade de software seguindo a **ISO/IEC 25010**.


