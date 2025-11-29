from flask import Flask, render_template, request, session, redirect, url_for
import pymongo
import os
from dotenv import load_dotenv
import bcrypt


load_dotenv()
app = Flask(__name__)

app.secret_key="gy6IJUcwHeZ7ygNY"

#Connecter a MongoDB
client = pymongo.MongoClient("mongodb+srv://gabrielfortoul4_db_user:gy6IJUcwHeZ7ygNY@annonce.4qw9vwk.mongodb.net/?retryWrites=true&w=majority&appName=Annonce")
db = client["SiteAnnonce"]

@app.route("/")
def index():
    annonce_data = list(db["Annonce"].find({})) #Je récupere tous les documents d'une collection
    if len(annonce_data) <= 0:
        return render_template("index.html", erreur = "Il n'y a pas encore d'annonce créer en une pour entamer un conversation")
    else:
        return render_template("index.html", annonce = annonce_data)

@app.route("/search", methods = ["GET"])
def search():
    query = request.args.get("q", "").strip()
    
    if query == "":
        results = list(db["Annonce"].find({}))
    else:
        results = list(db["Annonce"].find({
            "$or" : [
                {"titreAnnonce" : {"$regex" : query, "$options" : "i"}},
                {"textAnnonce" : {"$regex" : query, "$options" : "i"}},
                {"userAnnonce" : {"$regex" : query, "$options" : "i"}}
            ]
        }))
    if len(results) <= 0:
        return render_template("search_result.html", erreur = "Il n'y a pas de résultat pour ", query=query)    
    else:
        return render_template("search_result.html",erreur = "Voici les résultats pour ", annonce = results, query=query)    

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        db_users = db["User"]
        user = db_users.find_one({"userId" : request.form["utilisateur"]})
        if user:
            if request.form["mdp"] == user["userPassword"]:
                session["user"] = request.form["utilisateur"]
                return redirect(url_for('index'))
            else:
                return render_template("login.html", erreur = "Erreur : Mot de Passe Incorrect")
        else:
            return render_template("login.html", erreur = "Erreur : Nom d'Utilisateur Incorrect")    
    else:
        return render_template("login.html")  

@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == "POST":
        db_users = db["User"]
        if (db_users.find_one({"userId" : request.form["utilisateur"]})):
            return render_template("register.html", erreur = "Erreur : Le nom d'utilisateur existe déjà !")
        else:
            if(request.form["mdp"] == request.form["confirm_mdp"]):
                db_users.insert_one({
                    "userId" : request.form["utilisateur"],
                    "userPassword" : request.form["mdp"]
                })
                session["user"] = request.form["utilisateur"]
                return redirect(url_for('index'))
            else:
                return render_template("register.html", erreur = "Erreur : Les Mot de Passe ne sont pas identiques !")
    else:
        return render_template("register.html")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/publish", methods = ['POST', 'GET'])
def publish():
    if "user" not in session:
        return render_template("register.html")
    
    if request.method == "POST":
        db_annonces = db["Annonce"]
        titre = request.form["titre_annonce"]
        description = request.form["description"]
        auteur = session["user"]

        if titre and description:
            db_annonces.insert_one({
                "titreAnnonce" : titre,
                "textAnnonce" : description,
                "userAnnonce" : auteur
            })
            return redirect(url_for('index'))
        else:
            return render_template("publish.html", erreur = "Erreur : Veuillez remplir tous les champs obligatoires")    
    return render_template("publish.html")        

app.run(host="0.0.0.0", port=32768)