import random, database.database
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_session import Session
from PIL import Image
from database.database import thread_suppr, thread_clear, existe, add_friend, get_allfriends, replacePseudo, get_private_conversation_id, create_private_conversation, generate_conversation_id,add_message_to_private_conversation,get_last_messages_in_conversation
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = 'adfqsgERUEFB'
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.secret_key = "votre_clé_secrète"
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")
adminlist = ['maixins', "Nouxip"]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                             FONCTION UTILE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def checkisok():
  try:
    user = session['username']
    return False
  except:
    return True


def check_login(username, password):
  global session
  erreur, rep = database.database.login(username, password)
  if not username:
    return redirect(url_for("login"))
  if erreur == 0:

    session['username'] = username
    session['pdp'] = database.database.pdp_of(username)

    session['room_id'] = None
    print(session)

    return redirect(url_for("index"))

  elif erreur == 1:
    return redirect(url_for("login", info=rep))

  else:
    return redirect(url_for("login", info=rep))


def check_register(username, password):
  index, rep = database.database.register(username, password)
  if index == 0:
    session['username'] = username
    session['pdp'] = database.database.pdp_of(username)
    return redirect(url_for("index"))
  else:
    return redirect(url_for("login", info=rep))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                             SOCKET.IO
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@socketio.on('img')
def send_img(img):
  username = session['username']
  profile_pic_url = database.database.pdp_of(username)
  send({
      'username': username,
      'profile_pic': profile_pic_url,
      'content': img
  },
       broadcast=True)


@socketio.on('message')
def send_message(message):
  username = session['username']
  profile_pic_url = database.database.pdp_of(username)
  emit("message", {
      'username': username,
      'profile_pic': url_for('static', filename=f"temp-img/{profile_pic_url}"),
      'content': message
  },
       broadcast=True)
  database.database.send(username, message)


@socketio.on('clear')
def adminclear(data):
  global adminlist
  if session['username'] in adminlist:
    emit('clear', broadcast=True)
    thread_clear()
  else:
    print("")
    print("")
    print(session['username'], "a essayé de clear alors qu'il est pas moddé")
    print("")
    print("")


@socketio.on('suppr')
def adminsuppr(data):
  global adminlist
  print('suppr in comming')
  if session['username'] in adminlist:
    emit('suppr', broadcast=True)
    thread_suppr()
  else:
    print("")
    print("")
    print(session['username'], "a essayé de suppr alors qu'il est pas moddé")
    print("")
    print("")


@socketio.on('private_message')
def handle_private_message(data):
  room_id = data['room_id']
  message = data['message']
  username = session['username']
  profile_pic_url = database.database.pdp_of(username)

  messsages = {
    'name': username,
    'profile_pic': url_for('static', filename=f"temp-img/{profile_pic_url}"),
    'content': message
  }

  if not add_message_to_private_conversation(room_id,messsages):
    emit('private_message', 'refresh', to=room_id, broadcast=True)
    handle_private_message(data)

  emit('private_message', messsages, to=room_id, broadcast=True)


@socketio.on('join')
def join(conversation_id):
  try:
    if not session['room_id']:
      session['room_id'] = conversation_id
  except:
    print('bah la ta essayer de parler a deux personne en meme temps')
    leave(conversation_id)
    session['room_id'] = conversation_id
  finally:
    join_room(conversation_id)


@socketio.on('leave')
def leave(conversation_id):
  session['room_id'] = None
  leave_room(conversation_id)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                             @APP.ROUTE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@app.route("/", methods=["GET", "POST"])
def index():
  global adminlist
  if checkisok():
    return redirect(url_for("logout"))
  user = session["username"]
  session['pdp'] = database.database.pdp_of(session['username'])
  pdp = session['pdp']

  messages = database.database.get_last_messages()
  message_list = []
  for message in messages:
    message_list.append({
        "user": message['name'],
        "link": message["profile_pic"],
        "message": message["name"] + " : " + message["message"]
    })
  friends = get_allfriends(user)
  return render_template('index.html',
                         friends=friends,
                         ids=message_list,
                         username=user,
                         pdp=pdp,
                         admin=adminlist)


@app.route('/search', methods=['POST'])
def search():
  query = request.form['search']
  return f"{query}"


@app.route('/upload', methods=['POST', 'GET'])
def upload():
  checkisok()
  if 'file' not in request.files:
    return 'No file found'

  file = request.files['file']

  if file.filename == '':
    return redirect(url_for("test"))

  formatlist = ['.png', 'jpeg', '.jpg', '.JPG']
  if file.filename[::-1][0:4][::-1] not in formatlist:
    return "Mauvaise extension jpeg et png only"

  image = Image.open(file)
  image_size = image.size

  max_length = min(image_size)

  left = (image_size[0] - max_length) // 2
  top = (image_size[1] - max_length) // 2
  right = left + max_length
  bottom = top + max_length

  cropped_image = image.crop((left, top, right, bottom))

  resized_image = cropped_image.resize((300, 300))

  filename = f"{session['username']}_profile.png"

  resized_image.save(f"static/temp-img/{filename}")

  database.database.update_profile_picture(session['username'], filename)

  return redirect(url_for("index"))


@app.route("/login", methods=['GET', 'POST'])
def login():
  if 'username' in session:
    return redirect(url_for("index"))

  info = request.args.get('info', '')
  return render_template("login.html", info=info)


@app.route("/register", methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    if 'login_button' in request.form:

      username = request.form['username']
      password = request.form['password']
      print(username, password)
      return check_login(username, password)

    elif 'register_button' in request.form:
      username = request.form['username']
      password = request.form['password']
      return check_register(username, password)
  else:
    return render_template("register.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
  session.clear()
  return redirect(url_for("login"))


@app.route('/test')
def test():
  if checkisok():
    return redirect(url_for("logout"))
  pdp = session['pdp']
  user = session['username']
  return render_template("test.html", username=user, pdp=pdp)


@app.route('/profil')
def profil():
  if checkisok():
    return redirect(url_for("logout"))
  user = session['username']
  pdp = session['pdp']
  targetuser = request.args.get('targetuser')

  friends = get_allfriends(user)
  if targetuser and targetuser != user:
    if existe(targetuser):
      targetpdp = database.database.pdp_of(targetuser)
      return render_template('profilautre.html',
                             username=user,
                             pdp=pdp,
                             targetuser=targetuser,
                             targetpdp=targetpdp,
                             friends=friends)
    else:
      return render_template('profilpas.html',
                             username=user,
                             pdp=pdp,
                             friends=friends)
  else:
    return render_template("profil.html",
                           username=user,
                           pdp=pdp,
                           friends=friends)




@app.route('/addfriend', methods=['POST'])
def addfriend():
  checkisok()
  target = request.form['friend']
  user = session['username']
  add_friend(target, user)
  return 'has been send'


@app.route('/DM')
def DM():
  if checkisok():
    return redirect(url_for("logout"))

  user = session['username']
  pdp = session['pdp']
  target = request.args.get('target')
  participants = [user, target]
  room_id = get_private_conversation_id(participants)

  friends = get_allfriends(user)
  if not room_id:
    room_id = generate_conversation_id()
    create_private_conversation(generate_conversation_id(), participants)

  messages = get_last_messages_in_conversation(room_id)
  return render_template('DM.html',
                         pdp=pdp,
                         room_id=room_id,
                         username=user,
                         target=target,
                         friends=friends,
                         ids=messages)


@app.route('/changePseudo', methods=['POST'])
def changePseudo():
  newValue = request.args.get('new')
  if not existe(newValue):
    replacePseudo(session['username'], newValue)
    session['username'] = newValue
    return "200"
  else:
    return '409'

@app.route('/parametres')
def parametres():
  user = session['username']
  pdp = session['pdp']
  return render_template('parametres.html', pdp=pdp, username=user)

socketio.run(app, host='0.0.0.0', port=80, debug=True)


