import base64
import uuid
from datetime import datetime
from threading import Thread

import bcrypt
from tinydb import Query, TinyDB

db_account = TinyDB('database/db_account.json')
db_message = TinyDB("database/db_message.json")

db_messages_privates = TinyDB('database/db_messages_privates.json')
user = Query()


def register(name, mdp):
  result = db_account.search(user.name == name)
  if not len(result) > 0:
    if name[0].isalpha():
      hashed_password = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt())
      hashed_password_str = base64.b64encode(hashed_password).decode('utf-8')
      db_account.insert({
          "name": name,
          "mdp": hashed_password_str,
          "pdp_filename": "default.png",
          'friends': []
      })
      return 0, f"Bienvenue {name}!"
    else:
      return 1, f"{name} n'est pas valide, il faut que le premier caractère soit une lettre"
  else:
    return 2, f"Le nom d'utilisateur {name} est déjà pris"


def login(name, mdp):
  result = db_account.search(user.name == name)
  if len(result) == 0:
    return 2, "Nom d'utilisateur inconnu"
  else:
    stored_password_str = result[0]["mdp"]
    stored_password = base64.b64decode(stored_password_str.encode('utf-8'))
    if bcrypt.checkpw(mdp.encode('utf-8'), stored_password):
      return 0, f"Heureux de vous revoir {name}"
    else:
      return 1, "Je crains que vous vous êtes trompé de mot de passe"


def send(name, message):
  now = datetime.now()
  db_message.insert({
      "message": message,
      "date": now.strftime("%d/%m/%Y %H:%M:%S"),
      'profile_pic': pdp_of(name),
      "name": name
  })


def message_from(name):
  return db_message.search(user.name.all(name))


def pdp_of(name):
  return db_account.search(user.name == name)[0]["pdp_filename"]


def pdp_of_threading(name):
  return threading_process(pdp_of, name)


def threading_process(f, *args):
  t = Thread(target=f, args=args)
  t.run()

def send_to_thread(name, message):
  print(name, message)
  threading_process(send, name, message)

def update_profile_picture(username, image_filename):
  threading_process(update_pdp, username, image_filename)

def update_pdp(username, image_filename):
  db_account.update({'pdp_filename': image_filename}, user.name == username)

def get_last_messages():
  messages = db_message.all()[-25:]
  return messages

def _clear():
  messages = db_message.all()
  print(len(messages))
  if len(messages) <= 25:
    db_message.truncate()
  else:
    last_25_messages = messages[-25:]
    for message in last_25_messages:
      db_message.remove(doc_ids=[message.doc_id])

def suppr():
  messages = db_message.all()
  if messages:
    last_message_id = max((message.doc_id for message in messages))
    db_message.remove(doc_ids=[last_message_id])

def thread_suppr():
  threading_process(suppr)

def thread_clear():
  threading_process(_clear)

def existe(name):
  result = db_account.search(user.name == name)
  return len(result) > 0

def add_tag_to_all_users(tag):
  users = db_account.all()
  for user_data in users:
    username = user_data['name']
    db_account.update({tag: []}, user.name == username)

def add_friend(personne, ami):
  result = db_account.search(user.name == personne)
  amis = result[0].get('friends', [])
  if ami not in amis:
    amis.append(ami)
    db_account.update({'friends': amis}, user.name == personne)
  result_ami = db_account.search(user.name == ami)
  if result_ami:
    amis_ami = result_ami[0].get('friends', [])
    if personne not in amis_ami:
      amis_ami.append(personne)
      db_account.update({'friends': amis_ami}, user.name == ami)

def get_allfriends(personne):
  friends_list = []
  result = db_account.search(user.name == personne)
  if result:
    amis = result[0].get('friends', [])
    for ami in amis:
      friend_data = {'friendname': ami, 'friendpdp': pdp_of(ami)}
      friends_list.append(friend_data)
    return friends_list
  else:
    return []

def replacePseudo(old_username, new_username):
  conversations = db_messages_privates.search((Query().participants.any(old_username)))
  for conversation in conversations:
    updated_participants = [new_username if username == old_username else username for username in conversation['participants']]
    db_messages_privates.update({'participants': updated_participants}, Query().conversation_id == conversation['conversation_id'])


  messages = conversations

  for message in messages:
      updated_messages = []
      for msg in message['messages']:
          updated_name = new_username if msg['name'] == old_username else msg['name']
          msg['name'] = updated_name
          updated_messages.append(msg)

      message['messages'] = updated_messages

      db_messages_privates.update(message, Query().conversation_id == message['conversation_id'])

  db_account.update({'name': new_username}, user.name == old_username)

  user_data = db_account.search(user.name == new_username)
  friends = user_data[0].get('friends', [])

  updated_friends = []
  for friend in friends:
    friend_data = db_account.search(user.name == friend)
    if friend_data:
      friend_data[0]['friends'] = [
          new_username if name == old_username else name
          for name in friend_data[0].get('friends', [])
      ]
      updated_friends.append(friend_data[0])

  for friend_data in updated_friends:
    db_account.update({'friends': friend_data['friends']},
                      user.name == friend_data['name'])

  messages = db_message.search(user.name == old_username)

  for message in messages:
    db_message.update({'name': new_username}, user.name == old_username)

def create_private_conversation(conversation_id, participants):
  participants = sorted(participants)

  conversation = db_messages_privates.get(
      Query().conversation_id == conversation_id)
  if conversation:
    print(f"La conversation avec l'identifiant {conversation_id} existe déjà.")
    return
  else:
    new_conversation = {
        "conversation_id": conversation_id,
        "participants": participants,
        "messages": []
    }

    print(new_conversation)
    db_messages_privates.insert(new_conversation)
    print(f"Conversation privée avec l'identifiant {conversation_id} créée.")

def add_message_to_private_conversation(conversation_id, new_message):

  conversation = db_messages_privates.get(
      Query().conversation_id == conversation_id)

  if conversation:
    conversation["messages"].append(new_message)

    db_messages_privates.update(conversation,
                                Query().conversation_id == conversation_id)
    return True
  else:
    return False

def get_private_conversation_id(participants):
  sorted_participants = sorted(participants)

  conversation = db_messages_privates.get(
      Query().participants == sorted_participants)

  if conversation:
    return conversation["conversation_id"]
  else:
    return False

def generate_conversation_id():
  return str(uuid.uuid4())


def get_last_messages_in_conversation(conversation_id):
  num_messages = 20
  conversation = db_messages_privates.get(Query().conversation_id == conversation_id)

  if conversation:
      messages = conversation.get("messages", [])
      num_messages = min(num_messages, len(messages))
      last_messages = messages[-num_messages:]
      return last_messages
  else:
      return []