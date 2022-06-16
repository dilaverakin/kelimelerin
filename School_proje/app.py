from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,BooleanField,RadioField,SelectField
from passlib.hash import sha256_crypt
from wtforms.validators import *
from functools import wraps
import random

turkce = {}
englizce = {}

# Kullanıcı Giriş Decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapınız..","danger")
            return redirect(url_for("login"))
    return decorated_function

# Kullanıcı Çıkış kontrolu
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not("logged_in" in session):
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için Çıkış yapınız..","danger")
            return redirect(url_for("home"))
    return decorated_function


# kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("isim Soyisim",validators=[validators.length(min=4,max=25)])
    username = StringField("Kullanici Adi", validators=[validators.length(min=5, max=35)])
    email = StringField("Email Adresi",validators=[validators.Email(message="Lütfen geçerli bir email adresi giriniz.")])
    password = PasswordField("Paralo : ",validators=[
        DataRequired(message="Lütfen bir parola giriniz"),validators.EqualTo(fieldname="confirm",message="Parolaniz uyusmuyor...")

    ])
    confirm = PasswordField("Parola Doğrula :",validators=[validators.DataRequired(message="Bu alanı boş birakamazsiniz.")])

# Kullanıcı Giriş Formu
class loginForm(Form):
    username = StringField("Kullanıcı ismi : ",validators=[validators.DataRequired("Bu Alan Boş Bırakamazsınız!")])
    password = PasswordField("Parola : ",validators= [validators.DataRequired(message="Bu Alan Boş Bırakılamaz!")])


#Kelime Ekleme Formu
class wordaddForm(Form):
    enlgish = StringField("İngilizce ",validators=[validators.DataRequired("Bu alan Boş Bırakılamaz!")])
    Turkish = StringField("Türkçe ",validators=[validators.DataRequired("Bu alan Boş bırakılamaz!")])
    kategori = SelectField('Kategori', choices=[('Meyve', 'Meyve'), ('oyuncak', 'oyuncak'), ('Ev eşyası', 'Ev eşyası'),('Günlük','Günlük'),('Fiil','Fiil'),('isim','isim'),('Hayvan','Hayvan')])

app = Flask(__name__)
app.secret_key="scholl_proje"


"""SELECT `prefs` FROM `phpmyadmin`.`pma__table_uiprefs` WHERE `username` = 'root' AND `db_name` = 'deneme' AND `table_name` = 'users'"""
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "school_proje"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


#Canlı Ders
@app.route("/online")
def online():
    cursor = mysql.connection.cursor()
    sorgu = "SELECT * From words WHERE user = %s"
    cursor.execute(sorgu, (session["kullanıcı"],))
    result = cursor.fetchall()
    sayi = []
    for i in result:
        sayi.append(i)
    return render_template("online.html", result=result, sayi=sayi)

# change alanı
@app.route("/change")
def change():
    if session["change"]==True:
        session["change"]= False
    else:
        session["change"] = True
    return redirect(url_for("play"))



#Kontrol Et
@app.route("/kontrol/<string:id>")
def kontrol(id):
    cursor = mysql.connection.cursor()
    if not(session["degistir"]):
        sorgu = "Select * From words Where user = %s and english =%s and turkish = %s"
        result = cursor.execute(sorgu,(session["kullanıcı"],session["english"],session["kelime"]))
        if result>0:
            session["result"] = True
            return redirect(url_for("play"))
        else:
            session["result"] = False
            return redirect(url_for("play"))

    return redirect(url_for("play"))

#Kelime Oyunları
@app.route("/randint",methods=["GET","POST"])
def play():
    form =request.form
    is_wrong = False

    if request.method == "POST" and session["change"]:
        if session["change"]:
            ingilizce = form["ingilizce"]
            cursor = mysql.connection.cursor()
            sorgu1 = "Select * From words Where user = %s and english =%s and turkish = %s "
            cursor.execute(sorgu1,(session["kullanıcı"],ingilizce,session["t_kelime"]))
            result = cursor.fetchall()
            if len(result):
                flash("doğru","success")
            else:
                is_wrong = True
                flash("yanlış","danger")
    if request.method == "POST" and not(session["change"]):
            Turkce = form["Turkce"]
            cursor = mysql.connection.cursor()
            sorgu1 = "Select * From words Where user = %s and english =%s and turkish = %s "
            cursor.execute(sorgu1, (session["kullanıcı"],session["i_kelime"],Turkce))
            result = cursor.fetchall()
            if len(result):
                flash("doğru", "success")
            else:
                is_wrong = True
                flash("yanlış", "danger")
    cursor = mysql.connection.cursor()
    cursor.execute(("select * From words Where user = %s"),(session["kullanıcı"],))
    Kelimeler = cursor.fetchall()
    ingilizce = {}
    turkce =  {}
    id = []
    for Kelime in Kelimeler:
        ingilizce[Kelime["id"]] = Kelime["english"]
        turkce[Kelime["id"]] = Kelime["turkish"]
        id.append(Kelime["id"])
    rasgele = random.randint(0,len(id)-1)
    i_kelime = ingilizce[id[rasgele]]
    t_kelime = turkce[id[rasgele]]

    if is_wrong:
        t_kelime = session["t_kelime"]
        i_kelime = session["i_kelime"]

    session["i_kelime"] = i_kelime
    session["t_kelime"] = t_kelime
    session["degistir"]= True
    return render_template("index.html",i_kelime=i_kelime,t_kelime=t_kelime)


@app.route("/")
@login_required
def home():
    session["degistir"] = False
    session["ekle"]=False
    return render_template("index.html")

@app.route("/about")
def about():

    return render_template("about.html")
"""
#Kullanıcı girişi 2
@app.route("/login", methods = ["GET","POST"])
def kgiris():
    form = request.form
    session["change"] = True
    if request.method == "POST":
        username = form["kullanici_name"]
        password_entered = form["kullanici_password"]
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * From users WHERE username = %s"
        result = cursor.execute(sorgu, (username,))
        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered, real_password):
                flash("Başarı ile Giriş yaptınız", "success")
                session["kullanıcı"] = username
                session["logged_in"] = True
                return redirect(url_for("home"))
            else:
                flash("Şifrenizi kontorl edin", "danger")
                return redirect(url_for("login"))
        elif result == 0:
            flash("Kullanıcı Adınızı Kontrol ediniz..", "danger")
            return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))

    else:
        return render_template("kgiris.html" )
#Kullanıcı giriş

@app.route("/login", methods =["GET","POST"])
def login():
    session["change"] = True
    form = loginForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password_entered = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * From users WHERE username = %s"
        result = cursor.execute(sorgu,(username,))
        if result >0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarı ile Giriş yaptınız","success")
                session["kullanıcı"]=username
                session["logged_in"] = True
                return redirect(url_for("home"))
            else :
                flash("Şifrenizi kontorl edin","danger")
                return redirect(url_for("login"))
        elif result == 0 :
            flash("Kullanıcı Adınızı Kontrol ediniz..","danger")
            return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template(("login.html"),form = form)
"""
@app.route("/login", methods =["GET","POST"])
def login():
    session["change"] = True
    form = request.form
    if request.method == "POST" :
        username = form["kullanici_name"]
        password_entered = form["kullanici_password"]
        cursor = mysql.connection.cursor()
        sorgu = "SELECT * From users WHERE username = %s"
        result = cursor.execute(sorgu,(username,))
        if result >0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarı ile Giriş yaptınız","success")
                session["kullanıcı"]=username
                session["logged_in"] = True
                return redirect(url_for("home"))
            else :
                flash("Şifrenizi kontorl edin","danger")
                return redirect(url_for("login"))
        elif result == 0 :
            flash("Kullanıcı Adınızı Kontrol ediniz..","danger")
            return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template(("login.html"))
# dashboard paneli
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Bütün kelimeler
@app.route("/words")
def words():
    cursor= mysql.connection.cursor()
    sorgu ="SELECT * From words WHERE user = %s"
    cursor.execute(sorgu,(session["kullanıcı"],))
    result = cursor.fetchall()
    sayi = []
    for i in result:
        sayi.append(i)
    return render_template("words.html",result = result,sayi = sayi)

#Kelime Silme
@app.route("/delete/<string:id>")
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from words Where user = %s and id = %s"
    result = cursor.execute(sorgu,(session["kullanıcı"],id,))
    if result >0:
        sorgu2 = "Delete from words Where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla silindi","success")
        return redirect(url_for("words"))
    else:
        flash("Silerken Bir Sorun Yaşandı","danger")
        return redirect(url_for("words"))

#Kelime Ekle
@app.route("/add",methods=["GET","POST"])
def wordadd():
    form = wordaddForm(request.form)
    if request.method == "POST" :
        english = form.enlgish.data
        turkish = form.Turkish.data
        kategori = form.kategori.data
        user = session["kullanıcı"]
        cursor = mysql.connection.cursor()
        sorgu1 = "SELECT * From words WHERE user = %s"
        cursor.execute(sorgu1,(user,))
        result1 = cursor.fetchall()
        for i in result1:
            kullanıcı =i["user"]
            kelime1 = i["english"]
            kelime2 = i["turkish"]
            if kullanıcı == user and kelime1 == english and kelime2 == turkish:
                flash("bu kelime zaten ekli","danger")
                return render_template("index.html",form = form)
        sorgu = "INSERT INTO words(user,kategor,english,turkish) VALUES (%s,%s,%s,%s)"
        cursor.execute(sorgu,(user,kategori,english,turkish))
        mysql.connection.commit()
        cursor.close()
        flash("Kelimeniz Başarı ile Eklendi","success")
        return render_template("index.html",form =form)
    session["ekle"] = True
    session["degistir"] = False
    return render_template("index.html",form =form)

# kayıt olma
@app.route("/register",methods =["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():

        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        sorgu1 = "SELECT * From users WHERE username = %s"
        result = cursor.execute(sorgu1,(username,))

        if  result>0:
            flash("bu kullanıcı ismi ile kayıt yapamazsınız","danger")
            cursor.close()
            return redirect(url_for("register"))
        else:
            sorgu = "INSERT INTO users(name,email,username,password) VALUES (%s, %s, %s, %s)"
            cursor.execute(sorgu,(name,email,username,password))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for("home"))
    else:
        return render_template("register.html",form = form)

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
if __name__ == '__main__':
    app.debug = True
    app.run()



















