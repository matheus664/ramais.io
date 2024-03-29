from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, abort, jsonify, escape
import urllib.request , json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, create_engine, engine
from sqlalchemy.orm import sessionmaker
from flask_paginate import Pagination, get_page_args
import os, json
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl
import pandas as pd


# "sqlite:///cursos.sqlite3"
#mysql://root:tecnical@localhost/ramais"


app = Flask (__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config.from_object ('config')


db = SQLAlchemy(app)

ROWS_PER_PAGE = 10
ROWS_PER_PAGEADM = 20

TIPOS_DISPONIVEIS = set (['png', 'jpg', 'jpeg', 'gif', 'pdf', 'xlsx', 'aac', 'mp3'])



class ramais (db.Model):
    id = db.Column (db.Integer, primary_key = True)
    nome = db.Column (db.String(50))
    departamento = db.Column(db.String (100))
    ramal = db.Column (db.Integer)
    loja = db.Column (db.String(50))


    def __init__ (self, nome,departamento, ramal, loja):
        self.nome = nome
        self.departamento = departamento
        self.ramal = ramal
        self.loja = loja


class solicitacoes (db.Model):
    id = db.Column (db.Integer,primary_key = True)
    nome = db.Column (db.String(50)) 
    departamento = db.Column (db.String(100))
    ramal = db.Column (db.Integer)
    loja = db.Column (db.String(50))

    def __init__(self,nome,departamento,ramal,loja):
        self.nome = nome
        self.departamento = departamento
        self.ramal = ramal
        self.loja = loja

        


@app.route ('/')
def lista_ramais ():

    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page = ROWS_PER_PAGE)
    
    return render_template ('ramais.html', ramal = ramal)

@app.route ('/ramaisauth')
def lista_ramaisauth ():

    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page = ROWS_PER_PAGEADM)
    
    return render_template ('ramaisauth.html', ramal = ramal)


@app.route ('/ramais')
def lista_ramaiscard ():
    
    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    
    return render_template ('ramais.html', ramal=ramal)


    


@app.route ('/cria_ramal', methods = ["GET", "POST"])
def cria_ramal ():
    nome = request.form.get ('nome')
    departamento = request.form.get ('departamento')
    ramal = request.form.get ('ramal')
    loja = request.form.get ('loja')
    error = None

    if request.method == "POST":
        if not nome or not departamento or not ramal or not loja:
            flash ("Preencha todos os campos do formulário!", "error")
        else:
            ramal = ramais (nome, departamento, ramal, loja)
            db.session.add(ramal)
            db.session.commit()
            return redirect (url_for('lista_ramaisauth'))
    return render_template ('novo_ramal.html', error = error)



@app.route ('/solicitacoes', methods = ["GET","POST"])
def solicitacao_ramal ():
   
    page = request.args.get('page', 1, type=int)
    solicitacao = solicitacoes.query.paginate(page=page, per_page = ROWS_PER_PAGEADM)
    
    return render_template ('solicitacao_ramal.html', solicitacao=solicitacao)


@app.route ('/<int:id>/altera_ramal',methods = ["GET", "POST"])
def altera_ramal(id):
    solicitacao = solicitacoes.query.filter_by (id=id).first()
    ramal = ramais.query.filter_by (id=id).first()
    if request.method == "POST":
        nome = request.form ["nome"]
        departamento = request.form ["departamento"]
        ramal = request.form ["ramal"]
        loja = request.form ["loja"]
        ramais.query.filter_by (id=id).update ({"nome":nome,"departamento":departamento, "ramal":ramal,"loja":loja})
        db.session.delete(solicitacao)
        db.session.commit ()
        flash ("Dados atualizados com sucesso!")

    
    return render_template ("atualiza_solicitacao.html",solicitacao=solicitacao)



@app.route ('/<int:id>/atualiza_ramal', methods = ["GET", "POST"])
def atualiza_ramal (id):
    ramal =       ramais.query.filter_by (id=id).first()
    if request.method == "POST":
        nome = request.form ["nome"]
        departamento = request.form ["departamento"]
        ramal = request.form ["ramal"]
        loja = request.form ["loja"]
        ramais.query.filter_by (id=id).update ({"nome":nome,"departamento":departamento, "ramal":ramal,"loja":loja})
        db.session.commit ()
        flash ("Dados atualizados com sucesso!")
        return redirect (url_for ('lista_ramaisauth'))

    return render_template ("atualiza_ramal.html", ramal=ramal)







    


@app.route ('/<int:id>/remove_ramal', methods = ["GET", "POST"])
def remove_ramal (id):

    ramal = ramais.query.filter_by (id=id).first()
    db.session.delete(ramal)
    db.session.commit()
    flash ("Dados excluídos com sucesso!")
    return redirect (url_for('lista_ramaisauth'))


@app.route ('/<int:id>/remove_solicitacao', methods = ["GET", "POST"])
def remove_solicitacao (id):

    solicitacao = solicitacoes.query.filter_by (id=id).first()
    db.session.delete(solicitacao)
    db.session.commit()
    flash ("Dados excluídos com sucesso!")
    return redirect (url_for('lista_ramaisauth'))


@app.route ('/results', methods = ["GET","POST"])
def pesquisar ():
    resultado = request.form.get ("search")
    if resultado == '':
        return render_template ("erro.html")
    else :
        pesquisa = "{}".format(resultado)
        upperpesquisa = pesquisa.upper()
        convert = upperpesquisa, pesquisa
        print (convert) 
        nome = ramais.query.filter(ramais.nome.like (upperpesquisa)).all()
        departamento = ramais.query.filter (ramais.departamento.like(upperpesquisa)).all()
        ramal = ramais.query.filter(ramais.ramal.like(upperpesquisa)).all()
        loja = ramais.query.filter (ramais.loja.like(upperpesquisa)).all() 

    
    return render_template ('retorno_ramal.html', nome=nome, departamento=departamento, ramal=ramal, loja=loja)


@app.route ('/resultscard', methods = ["GET","POST"])
def pesquisarcard ():
    resultado = request.form.get ("search")
    if resultado == '':
        return render_template ("erro.html")
    else :
        pesquisa = "{}".format(resultado)
        nome = ramais.query.filter(ramais.nome.like (pesquisa)).all()
        departamento = ramais.query.filter (ramais.departamento.like(pesquisa)).all()
        ramal = ramais.query.filter(ramais.ramal.like(pesquisa)).all()
        loja = ramais.query.filter (ramais.loja.like(pesquisa)).all() 

    
    return render_template ('retorno_ramalcard.html', nome=nome, departamento=departamento, ramal=ramal, loja=loja)


@app.route ('/resultsadmin', methods = ["GET", "POST"])
def pesquisaradm():
    resultado = request.form.get ("search2")
    if resultado == '':
        return render_template ("erro.html")
    else:
        pesquisa = "{}".format(resultado)
        nome = ramais.query.filter(ramais.nome.like(pesquisa)).all()
        departamento = ramais.query.filter(ramais.departamento.like(pesquisa)).all()
        ramal = ramais.query.filter(ramais.ramal.like(pesquisa)).all()
        loja = ramais.query.filter(ramais.loja.like(pesquisa)).all()
        
    return render_template ("retorno_ramaladmin.html", nome=nome, departamento=departamento, ramal=ramal, loja=loja)

@app.route ('/admin', methods = ["GET", "POST"])
def login ():
    if request.method == "POST":
        usuario = request.form.get ("usuario")
        senha   = request.form.get ("senha")
        if usuario == "admin" and senha == "admin":
                return redirect (url_for('admramal'))
        elif usuario == '':
            flash ("Campo 'Usuário' vazio, preencha para ter acesso!")
        elif senha == '':
            flash ("Campo 'Senha' vazio, preencha para ter acesso!")
        elif usuario == '' and senha == '':
            flash ("Insira credenciais para Usuário e Senha para Continuar!")
        else :
            flash ("Caro administrador, credenciais incorretas, tente novamente!")
        
    
    
    return render_template ('admin.html')


@app.route ('/admramal', methods = ["GET", "POST"])
def admramal ():
    page = request.args.get('page', 1, type=int)
    ramal = ramais.query.paginate(page=page, per_page = ROWS_PER_PAGEADM)
    
    return render_template ('ramaisauth.html', ramal = ramal)


def arquivos_permitidos (filename):
    return '.' in filename and filename.rsplit ('.',1)[1].lower () in TIPOS_DISPONIVEIS


@app.route ('/upload')
def home ():
    return render_template('upload.html')

@app.route ('/upload', methods = ["POST"])
def upload_image ():
    file = request.files ["file"]
    if file.filename == '':
        flash("Nenhum arquivo selecionado")
        return redirect(request.url)
    if not arquivos_permitidos(file.filename):
        flash("Utilize os tipos de arquivos permitidos")
        abort (401)
        
    filename = str (uuid.uuid4())
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    flash("Arquivo enviado com sucesso!")
    return render_template('upload.html', filename=filename)

@app.route ('/display/<filename>')
def display_image (filename):
    return redirect(url_for('static', filename = 'uploads/' + filename), code = 301)


@app.route('/search')
def upload_form():
	return render_template('autocomplete.html')

@app.route('/search', methods=['POST'])
def search():
    term = request.form['q']
    substring = term [0:1]
    caps = substring.upper()
    string = term [1 :]
    stringfull = caps+string
    print ('term: ', stringfull)	
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "results.json")
    json_data = json.loads(open(json_url).read())
	#print (json_data)
	#print (json_data[0])
	
    filtered_dict = [v for v in json_data if stringfull in v]	
	#print(filtered_dict)
	
    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp


@app.route ('/<int:id>/sugerir_ramal',  methods = ["GET", "POST"])
def sugerir_ramal (id):
    ramal = ramais.query.filter_by (id=id).first()
    solicitacao =  solicitacoes.query.filter_by (id=id).first()
    if request.method == "POST":
        nome = request.form ["nome"]
        departamento = request.form ["departamento"]
        ramal = request.form ["ramal"]
        loja = request.form ["loja"]
        if not nome or not departamento or not ramal or not loja:
            flash ("Preencha todos os campos do formulário!", "error")
        else:
            solicitacao = solicitacoes (nome, departamento, ramal, loja)
            db.session.add(solicitacao)
            db.session.commit()
        # Define the HTML document
        html = ''' 
            <html>
                <body>
                    <h2 style ="color:blue;">Nova Sugestão de Ramal!</h2>
                <a href="http://10.3.149.105:552/admramal" type="submit">Visualizar</a>
                </body>
            </html>
                '''

        # Set up the email addresses and password. Please replace below with your email address and password
        email_from = 'ramais@grupometronorte.com.br'
        password = 'Metro@12'
        email_to = 'ramais@grupometronorte.com.br'

        # Generate today's date to be included in the email Subject
        date_str = pd.Timestamp.today().strftime('%Y-%m-%d')
        nome1=f'Nome:{nome}\n'
        departamento1=f'Departamento:{departamento}\n'
        ramal1=f'Ramal:{ramal}\n'
        loja1=f'Revenda:{loja}'
        


        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart("plain")
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = f'Nova Solicitação - {date_str}'

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))
        email_message.attach(MIMEText(nome1, "plain"))
        email_message.attach(MIMEText(departamento1, "plain"))
        email_message.attach(MIMEText(ramal1, "plain"))
        email_message.attach(MIMEText(loja1, "plain" ))
        
        # Convert it as a string
        email_string = email_message.as_string()

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.grupometronorte.com.br", 587) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_string)
            flash ("Dados enviados ao Administrador!")
            return redirect (url_for('lista_ramaiscard'))
        

    return render_template ("sugerir_ramal.html", ramal=ramal)




if __name__ == '__main__':
    # website_url = 'metronorte.io:552'
    # app.config['SERVER_NAME'] = website_url

    app.run()