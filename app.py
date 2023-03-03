from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
import urllib.request , json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, create_engine, engine
from sqlalchemy.orm import sessionmaker
from flask_paginate import Pagination, get_page_parameter

# "sqlite:///cursos.sqlite3"

app = Flask (__name__)





app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:tecnical@localhost/ramais"

db = SQLAlchemy(app)

frutas = []
#dentro da lista tem um dicionario
registros = []

class cursos (db.Model):
    id = db.Column (db.Integer, primary_key = True)
    nome = db.Column (db.String (50))
    descricao = db.Column (db.String (100))
    ch = db.Column (db.Integer)

    def __init__(self, nome, descricao, ch):
        self.nome = nome
        self.descricao = descricao
        self.ch = ch

class ramais (db.Model):
    id = db.Column (db.Integer, primary_key = True)
    nome = db.Column (db.String(50))
    departamento = db.Column(db.String (100))
    ramal = db.Column (db.Integer)
    loja = db.Column (db.String(50))
    ativo = db.Column (db.Integer)
    foto = db.Column (db.String(50))
    




    def __init__ (self, nome,departamento, ramal, loja, ativo, foto):
        self.nome = nome
        self.departamento = departamento
        self.ramal = ramal
        self.loja = loja
        self.ativo = ativo
        self.foto = foto






@app.route ('/', methods = ["GET", "POST"])
def index ():
    
    #frutas = ['Morango','Uva','Maça','Laranja','Limao', 'Caqui', 'Carambola']
    
    if request.method == "POST" :
        if request.form.get("fruta"):
            frutas.append(request.form.get("fruta"))
    return render_template ("index.html",frutas=frutas)



@app.route ('/sobre', methods = ["GET", "POST"])
def sobre ():

    #notas = {'Matheus Lopes':5.0, 'Paulo Silva':6.0, 'Aluno':7.0, 'Julia Costa':8.5,'Rafael Pedro':10.0}
    if request.method == "POST":
        if request.form.get("aluno") and request.form.get ("nota"):
            registros.append ({"aluno": request.form.get("aluno"),"nota": request.form.get("nota")})
    return render_template ('sobre.html', registros=registros)


@app.route ('/filmes/<propriedade>')
def filmes (propriedade):

    if propriedade == 'populares':
        url = 'https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key=550917c52b3d7ebdbd27dc4cfd3c2815'
    elif propriedade == 'kids':
        url = 'https://api.themoviedb.org/3/discover/movie?certification_country=US&certification.lte=G&sort_by=popularity.desc&api_key=550917c52b3d7ebdbd27dc4cfd3c2815'
    elif propriedade == '2010':
        url = 'https://api.themoviedb.org/3/discover/movie?primary_release_year=2010&sort_by=vote_average.desc&api_key=550917c52b3d7ebdbd27dc4cfd3c2815'
    elif propriedade == 'drama':
        url = 'https://api.themoviedb.org/3/discover/movie?with_genres=18&primary_release_year=2014&api_key=550917c52b3d7ebdbd27dc4cfd3c2815'
    elif propriedade == 'tom_cruise':
        url = 'https://api.themoviedb.org/3/discover/movie?with_genres=878&with_cast=500&sort_by=vote_average.desc&api_key=550917c52b3d7ebdbd27dc4cfd3c2815'
    elif propriedade == 'Rooney Mara':
        url = "https://api.themoviedb.org/3/discover/movie?with_people=108916,7467&sort_by=popularity.desc&api_key=550917c52b3d7ebdbd27dc4cfd3c2815"
    resposta = urllib.request.urlopen(url)


    dados = resposta.read()
    jsondata = json.loads(dados)

    return render_template ("filmes.html", filmes=jsondata ['results'])

@app.route ('/cursos')
def lista_cursos ():
    # page = request.args.get ("page", 1, type=int)
    # per_page = 100
    # todos_cursos = cursos.query.paginate(page, per_page)
    return render_template ('cursos.html', cursos=cursos.query.all())

@app.route ('/ramais')
def lista_ramais ():


    return render_template ('ramais.html', ramais=ramais.query.filter(ramais.ramal != '', ramais.departamento != '', ramais.ativo != 0).order_by(ramais.id).limit(6))



@app.route ('/cria_curso', methods = ["GET", "POST"])
def cria_curso():
    nome = request.form.get ('nome')
    descricao = request.form.get ('descricao')
    ch = request.form.get ('ch')
    error = None

    if request.method == "POST":
        if not nome or not descricao or not ch:
            flash ("Preencha todos os campos do Formulário!", "error")
        else:
            curso = cursos(nome, descricao, ch)
            db.session.add(curso)
            db.session.commit()
            return redirect (url_for ('lista_cursos'))
    return render_template ('novo_curso.html', error = error)



@app.route ('/page1', methods = ["GET", "POST"])
def paginate ():
    ramal = ramais.query.filter(ramais.ramal != '', ramais.departamento != '', ramais.ativo != 0).order_by(ramais.id).limit(6)
    return render_template('ramais.html', ramal=ramal)



@app.route ('/cria_ramal', methods = ["GET", "POST"])
def cria_ramal ():
    nome = request.form.get ('nome')
    departamento = request.form.get ('departamento')
    ramal = request.form.get ('ramal')
    loja = request.form.get ('loja')
    error = None

    if request.method == "POST":
        if not nome or not departamento or not ramal or not loja :
            print (nome, departamento, ramal, loja)
            flash ("Preencha todos os campos do formulário!", "error")
        else:
            ramal = ramais (nome, departamento, ramal, loja)
            db.session.add(ramal)
            db.session.commit()
            return redirect (url_for('lista_ramais'))
    return render_template ('novo_ramal.html', error = error)



@app.route ('/<int:id>/atualiza_curso',  methods = ["GET", "POST"])
def atualiza_curso (id):
    curso = cursos.query.filter_by (id=id).first()
    if request.method == "POST":
        nome = request.form ["nome"]
        descricao = request.form ["descricao"]
        ch = request.form ["ch"]

        cursos.query.filter_by (id=id).update ({"nome":nome, "descricao":descricao, "ch":ch})
        db.session.commit ()
        return redirect (url_for('lista_cursos'))

    return render_template ("atualiza_curso.html", curso=curso)
    print(curso)


@app.route ('/<int:id>/atualiza_ramal', methods = ["GET", "POST"])
def atualiza_ramal (id):
    ramal = ramais.query.filter_by (id=id).first()
    if request.method == "POST":
        nome = request.form ["nome"]
        departamento = request.form ["departamento"]
        ramal = request.form ["ramal"]
        loja = request.form ["loja"]

        ramais.query.filter_by (id=id).update ({"nome":nome,"departamento":departamento, "ramal":ramal,"loja":loja})
        db.session.commit ()
        return redirect (url_for ('lista_ramais'))

    return render_template ("atualiza_ramal.html", ramal=ramal)

    


@app.route ('/<int:id>/remove_curso', methods = ["GET", "POST"])
def remove_curso (id):
    
    curso = cursos.query.filter_by (id=id).first()
    db.session.delete(curso)
    db.session.commit()
    return redirect (url_for('lista_cursos'))


@app.route ('/<int:id>/remove_ramal', methods =["GET", "POST"])
def remove_ramal (id):

    ramal = ramais.query.filter_by (id=id).first()
    db.session.delete(ramal)
    db.session.commit()
    return redirect (url_for('lista_ramais'))













with app.app_context():
    db.create_all()

app.run(debug=True)