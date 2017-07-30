import random #generowanie liczb losowych
import os #do pracy na katalogach i listach plików
import hashlib #do szyfrowania plików
import logging
import sys

from datetime import datetime #praca z datą
from flask import Flask, request, render_template, session, redirect
'''request do pobierania danych z html
render_template do wyświetlania html z katalogu templates
session do przekazywania parametrów między sesjami (dane logowania)
'''

app = Flask(__name__)
app.secret_key = 'enigma'

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

@app.route('/')
def initial():
    return render_template('index.html')


@app.route("/dice", methods=['GET', 'POST'])
def kosci():
    if request.method == 'POST':
        rzut=request.form['answer']
        indexD = rzut.find('d') if 'd' in rzut else rzut.find('D')
        index_sign = rzut.find('-') if rzut.find('-') > rzut.find('+') else rzut.find('+')

        print(rzut, " ", indexD, " ", index_sign)

        il_rzut = int(rzut[:indexD]) if indexD != 0 else 1

        if index_sign == -1:
            mod = 0
            typ = int(rzut[indexD+1:])
        else:
            mod = int(rzut[index_sign:])
            typ = int(rzut[indexD+1:index_sign])

        wynik = sum((random.randint(1, typ) for i in range (il_rzut))) + mod
        return render_template('kosci.html', wartosc=wynik)
    else:
        return render_template('kosci.html', wartosc=0)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form['login'] + '.txt'
        user_pass = hashlib.md5(request.form['pass'].encode()).hexdigest()
        list_users = os.listdir("Users/")
        if user_login in list_users:
            file_pass = open("Users/" + user_login, 'r').read()
            #close("Users/" + user_login)
            if file_pass == user_pass:
                session['user'] = user_login
                return redirect('blog')
            else:
                return render_template('login.html', tytul='Hasło niepoprawne')
        else:
            return render_template('login.html', tytul='Nie ma takiego loginu')
    else:
        return render_template('login.html', tytul='Wpisz login i hasło')


@app.route("/blog", methods=['GET',  'POST'])
def blog():
    if 'user' in session:
        if request.method == 'POST':
            file_list = os.listdir("templates/files_blog/")
            tytul = request.form['title']
            content = request.form['content']
            if tytul+'.txt' in file_list:
                return render_template('blog.html', tytul='Zmień tytuł artykułu', tresc=content)
            else:
                plik = open("templates/files_blog/" + tytul + ".txt", 'w')
                plik.write(content + '\n'+ session['user'] +'\n'+ str(datetime.now()))
                plik.close()
                return render_template('blog.html', tytul='Artykuł został zapisany. Wpisz następny')
        else:
            return render_template('blog.html', tytul='blog ' + session['user'])
    else:
        return redirect('login')

@app.route("/logout")
def logout():
    user_temp=session['user']
    session.pop('user', None)
    return user_temp +' został wylogowany'

@app.route("/bloglist")
def bloglist():
    if 'user' in session:
        file_list = os.listdir("templates/files_blog/")
        insert_html = []
        for i in file_list:
            insert_html.append(str('<p><a href="/read_article/' + i + '">' + i + '</a></p>'))
            tekst_check = str(''.join(insert_html))
        return render_template('bloglist.html', tytul='lista blogow', odnosniki=tekst_check, link_blog=file_list)
                #str(''.join(insert_html))#
    else:
        return redirect('login')

@app.route("/read_article/<tytul>")
def wyswietl (tytul):
    tekst_print = open(str('templates/files_blog/' + tytul), 'r').read()
    return tekst_print

@app.route("/new_user", methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            user_login = request.form['login']
            user_pass = hashlib.md5(request.form['pass'].encode()).hexdigest()
            list_users = os.listdir("Users/")
            if user_login in list_users:
                return render_template('login.html', tytul='Użytkownik o takim loginie już istnieje, zmień login')
            else:
                plik = open("Users/" + user_login +'.txt', 'w')
                plik.write(user_pass)
                plik.close()
                return redirect('login')
        except Exception as e:
            text_blad =str('%s %s' % (type(e), e))
            return text_blad
    else:
        return render_template('login.html', tytul='Podaj login i hasło')


@app.route("/test", methods=['GET', 'POST'])
def test():
    test_txt = os.path.dirname(__file__)
    return test_txt



if __name__ == "__main__":
    app.run(debug=True)
