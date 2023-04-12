from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, abort
import urllib.request , json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, create_engine, engine
from sqlalchemy.orm import sessionmaker
from flask_paginate import Pagination, get_page_args

# "sqlite:///cursos.sqlite3"
#mysql://root:tecnical@localhost/ramais"


app = Flask (__name__)





app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@localhost/ramais"

db = SQLAlchemy(app)



class ramais (db.Model):
    id = db.Column (db.Integer, primary_key = True)
    nome = db.Column (db.String(50))
    departamento = db.Column(db.String (100))
    ramal = db.Column (db.Integer)
    loja = db.Column (db.String(50))
    
    




    def __init__ (self, nome,departamento, ramal, loja, ativo):
        self.nome = nome
        self.departamento = departamento
        self.ramal = ramal
        self.loja = loja
        

ROWS_PER_PAGE = 6

@app.route ('/')
def lista_ramais ():

    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page = ROWS_PER_PAGE)
    
    return render_template ('ramais.html', ramal = ramal)

@app.route ('/ramaisauth')
def lista_ramaisauth ():

    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page = ROWS_PER_PAGE)
    
    return render_template ('ramaisauth.html', ramal = ramal)

    


@app.route ('/cria_ramal', methods = ["GET", "POST"])
def cria_ramal ():
    nome = request.form.get ('nome')
    departamento = request.form.get ('departamento')
    ramal = request.form.get ('ramal')
    loja = request.form.get ('loja')
    ativo = request.form.get ('ativo')
    error = None

    if request.method == "POST":
        if not nome or not departamento or not ramal or not loja:
            flash ("Preencha todos os campos do formulário!", "error")
        else:
            ramal = ramais (nome, departamento, ramal, loja, ativo)
            db.session.add(ramal)
            db.session.commit()
            return redirect (url_for('lista_ramais'))
    return render_template ('novo_ramal.html', error = error)



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

    


@app.route ('/<int:id>/remove_ramal', methods =["GET", "POST"])
def remove_ramal (id):

    ramal = ramais.query.filter_by (id=id).first()
    db.session.delete(ramal)
    db.session.commit()
    return redirect (url_for('lista_ramais'))


@app.route ('/results', methods = ["GET","POST"])
def pesquisar ():
    resultado = request.form.get ("search")
    pesquisa = "{}".format(resultado)
    ramal = ramais.query.filter(ramais.nome.like (pesquisa)).all()
    
    return render_template ('retorno_ramal.html', ramal = ramal)


@app.route ('/admin', methods = ["GET", "POST"])
def login ():
    if request.method == "POST":
        usuario = request.form.get ("usuario")
        senha = request.form.get ("senha")
        if usuario == "admin" and senha == "admin":
                return redirect (url_for('admramal'))
        else :
            abort (401)
    
    
    return render_template ('admin.html')


@app.route ('/admramal', methods = ["GET", "POST"])
def admramal ():
    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page = ROWS_PER_PAGE)
    
    return render_template ('ramaisauth.html', ramal = ramal)


 



with app.app_context():
    db.create_all()

app.run(debug=True, host = "127.0.0.1", port = "552")