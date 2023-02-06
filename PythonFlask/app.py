# Ativar o ambiente de execução: .venv\Scripts\Activate.ps1
# Tutorial muito bom: https://code.visualstudio.com/docs/python/tutorial-flask

from flask import Flask, render_template, request, redirect, url_for, flash 
import urllib.request, json
from flask_sqlalchemy import SQLAlchemy

######################## BANCO DE DADOS ############################################

# Criar um app do SQLAlchemy e passar nosso "app.py" como parâmetro:
db = SQLAlchemy()

# Meu app: parâmetro name
app = Flask(__name__) 

# Definir o BD (sqlite); onde ele se encontra (raiz do projeto); e o nome do BD (cursos.sqlite3):
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cursos_sqlite3.db"

# initialize the app with the extension
db.init_app(app)

# Classe cursos do BD (tabela "cursos"):
class cursos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    descricao = db.Column(db.String(100))
    ch = db.Column(db.Integer)

    # Método construtor da classe (auxilia quando estivermos inserindo informações no BD):
    def __init__(self, nome, descricao, ch):
        self.nome = nome
        self.descricao = descricao
        self.ch = ch    
    
######################## URL home ############################################
'''
1º)Definir a rota:
"route" para o "app".
Por padrão, o flask roda na porta 5000: http://127.0.0.1:5000
Barra é a rota principal.

2º) Definir uma função que será processada na rota definida anteriormente.
'''
# Lista (forma dinâmica) - lista vazia:
frutas = []
registros = []


@app.route("/", methods=["GET","POST"])
def home():
    # Lista - pode conter vários tipos de dados (forma estática):
    #cats = ["Amarelo","Ariel","Bruce","Darth"]    

    if request.method == "POST":
        if request.form.get("fruta"):
            frutas.append(request.form.get("fruta"))
    # "render_template" retorna uma página HTML:
    return render_template("index.html", frutas=frutas)

######################## URL sobre ############################################

@app.route("/sobre", methods=["GET","POST"])
def sobre():
    #notas = {"Amarelo":9.9, "Lana":10.0, "Mia":9.2, "Zeus":10.0, "Zoe":10.0}
    if request.method == "POST":
        if request.form.get("aluno") and request.form.get("nota"):
            registros.append({"aluno":request.form.get("aluno"), "nota":request.form.get("nota")})
    return render_template("sobre.html", registros=registros)

######################## URL filmes e suas propriedades ############################################

@app.route('/filmes/<propriedade>')
def filmes(propriedade):

    if propriedade == 'populares': 
        # URL de filmes mais populares: 
        url = 'https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key=f77a1348eeabba3f19e8d5deb63f3452'
    
    elif propriedade == 'kids': 
        # URL de filmes kids: 
        url = 'https://api.themoviedb.org/3/discover/movie?certification_country=US&certification.lte=G&sort_by=popularity.desc&api_key=f77a1348eeabba3f19e8d5deb63f3452'
    
    elif propriedade == '2010': 
        # URL de filmes 2010: 
        url = 'https://api.themoviedb.org/3/discover/movie?primary_release_year=2010&sort_by=vote_average.desc&api_key=f77a1348eeabba3f19e8d5deb63f3452'
    
    elif propriedade == 'drama': 
        # URL de filmes drama: 
        url = 'https://api.themoviedb.org/3/discover/movie?with_genres=18&sort_by=vote_average.desc&vote_count.gte=10&api_key=f77a1348eeabba3f19e8d5deb63f3452'
    
    elif propriedade == 'tom_cruise': 
        # URL de filmes tom_cruise: 
        url = 'https://api.themoviedb.org/3/discover/movie?with_genres=878&with_cast=500&sort_by=vote_average.desc&api_key=f77a1348eeabba3f19e8d5deb63f3452'
    
    elif propriedade == 'comedia':
        # URL de filmes de comedia:
        url = 'https://api.themoviedb.org/3/discover/movie?with_genres=35&with_cast=23659&sort_by=revenue.desc&api_key=f77a1348eeabba3f19e8d5deb63f3452'

    
    # Requisição para abrir a URL:
    resposta = urllib.request.urlopen(url)

    # Ler os dados que estão na URL:
    dados = resposta.read()

    # Converter os dados para o formato JSON:
    jsondata = json.loads(dados)

    # Retornar somente os resultados:
    return render_template("filmes.html", filmes=jsondata['results'])

######################## URL cursos #################################################

@app.route('/cursos')
def lista_cursos():
    # Paginação - cada página terá de 1 a 4 cursos:
    page = request.args.get('page', 1, type=int)
    per_page = 4
    todos_cursos = cursos.query.paginate(page=page, per_page=per_page)
    return render_template("cursos.html",cursos=todos_cursos)

######################## URL cria_cursos ############################################

@app.route('/cria_cursos', methods=["GET","POST"])
def cria_cursos():
    # Recuperar os dados inseridos no formulário "<form>" da página "novo_curso.html":
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    ch = request.form.get('ch')

    # Verificar se o método que está sendo chamado/disparado na requisição é o método POST:
    if request.method == 'POST':
        # Validar os dados no servidor (flash):
        if not nome or not descricao or not ch:
            flash("Preencha todos os campos do formulário", "error")
        else:
            # Tabela "cursos" e o método construtor:
            curso = cursos(nome, descricao, ch)      
        
            # Adicionar no BD:
            db.session.add(curso)

            # Dar um commit para salvar os valores inseridos:
            db.session.commit()

            # Retorna para a página "lista_cursos.html":
            return redirect(url_for('lista_cursos'))
    return render_template("novo_curso.html")

######################## URL '/<int:id>/atualiza_curso' ###########################
# Quando precisar criar/editar algo, é necessário o "id":
# Propriedade: "id"
# Tipo: int
# Rota: /atualiza_curso
@app.route('/<int:id>/atualiza_curso', methods=["GET", "POST"])
def atualiza_curso(id):
    # Filtrar o curso pelo id (tabela curso) e pegar o primeiro registro:
    curso = cursos.query.filter_by(id=id).first()
    
    # Recuperar os valores:
    if request.method == 'POST':
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        ch = request.form["ch"]

        # Update para atualizar os dados:
        cursos.query.filter_by(id=id).update({"nome":nome, "descricao":descricao, "ch":ch})
        
        # Dar o commit, ou seja, atualizar no BD:
        db.session.commit()

        # Quando atualizar, retornar para a página de lista de cursos (cursos.html): 
        return redirect(url_for('lista_cursos'))
    # Retornar a página e o curso:
    return render_template("atualiza_curso.html", curso=curso)

######################## URL '/<int:id>/remove_curso' ###########################
# Concluir o CRUD (Create, Read, Update, Delete) é um acrônimo para as maneiras 
# de se operar em informação armazenada. Operações básicas utilizadas em BDs relacionais.

@app.route('/<int:id>/remove_curso')
def remove_curso(id):
    # Filtrar o curso pelo id (tabela curso) e pegar o primeiro registro:
    curso = cursos.query.filter_by(id=id).first()
    db.session.delete(curso)
    db.session.commit()
    return redirect(url_for('lista_cursos'))



with app.app_context():
    db.create_all()

#if __name__=="__main__":
#app.run(debug=True)