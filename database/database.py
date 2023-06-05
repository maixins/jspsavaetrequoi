from tinydb import TinyDB, Query
from tinydb.operations import add
from datetime import datetime

db_account = TinyDB('database/db_account.json')
db_message = TinyDB("database/db_message.json")
user = Query()


def register(name, mdp):
    result = db_account.search(user.name == name)
    if not len(result) > 0:
        if name[0].isalpha():
            db_account.insert({"name": name, "mdp": str(mdp), "message": [], "pdp_filename": "default.png"})
            return 0,f"Bienvenue {name}!"
        else:
            return 1,f"{name} n'est pas valide, il faut que le premier caractère soit une lettre"

    else:
        return 2,f"Le nom d'utilisateur {name} est déja pris"


def login(name,mdp):
    result = db_account.search(user.name == name)
    if len(result) == 0:
        return 2,f"Nom d'utilisateur inconnu"
    else:
        if result[0]["mdp"] == mdp:
            return 0,f"Heureux de vous revoir {name}"
        else:
            return 1,f"Je crains que vous vous êtes trompés de mot de passe"


def send(name, message):
    now = datetime.now()
    db_account.update(add("message", [{"message":message, "date":now.strftime("%d/%m/%Y %H:%M:%S")}]), user.name == name)
    db_message.insert({"message": message, "date": now.strftime("%d/%m/%Y %H:%M:%S"),'profile_pic':pdp_of(name) ,"name": name})



def message_from(name):
    return db_message.search(user.name.all(name))


def pdp_of(name):
  return db_account.search(user.name == name)[0]["pdp_filename"]

def update_profile_picture(username, image_filename):
    db_account.update({'pdp_filename': image_filename}, user.name == username)


def get_last_messages():
    messages = db_message.all()[-25:]
    return messages


