import random,database.database 
from flask_socketio import SocketIO, emit, send
from flask import Flask, render_template, request, url_for, redirect, flash, session
from PIL import Image


app = Flask(__name__)
app.config["SECRET_KEY"] = 'adfqsgERUEFB'
app.secret_key = "votre_clé_secrète"
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/", methods=["GET","POST"])
def index():
    print(request.remote_addr,session)
    print()
    if not 'username' in session:
      return redirect(url_for("login")) 
    user = session["username"]
    session['pdp'] = database.database.pdp_of(session['username'])
    pdp = session['pdp']
  
    messages = database.database.get_last_messages()
    message_list = []
    for message in messages:
        message_list.append({
            "link": message["profile_pic"],
            "message": message["name"]+" : "+message["message"]
        })
      
    return render_template('index.html', ids=message_list,username=user,pdp=pdp)


@app.route("/change")
def change():
  return render_template('change.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['search']
    return f"{query}"



@app.route('/upload', methods=['POST','GET'])
def upload():
    if 'username' not in session:
        return redirect(url_for("login"))

    if 'file' not in request.files:
        return 'No file found'

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for("test"))

    formatlist = ['.png', 'jpeg', '.jpg','.JPG']
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
            return check_login(username,password)

        elif 'register_button' in request.form:
            username = request.form['username']
            password = request.form['password']
            return check_register(username,password)
    

def check_login(username,password):
    erreur, rep = database.database.login(username,password)
    if not username:
        return redirect(url_for("login")) 
    if erreur == 0:

        session['username'] = username
        session['pdp'] = database.database.pdp_of(username)
        return redirect(url_for("index"))  
      
    elif erreur == 1:
        return redirect(url_for("login", info=rep)) 
      
    else:
        return redirect(url_for("login", info=rep)) 


def check_register(username,password):
    index, rep = database.database.register(username, password)
    if index ==0:
        session['username'] = username
        session['pdp'] = database.database.pdp_of(username)
        return redirect(url_for("index"))
    else:
      return redirect(url_for("login", info=rep))



@app.route("/logout", methods=["GET","POST"])
def logout():
  session.pop('username', None)
  return redirect(url_for("login"))


@socketio.on('message')
def send_message(message):
    username = session['username']
    profile_pic_url = database.database.pdp_of(username) 
    index = message.find(':')
    content = message[index+1:].strip() 
    send({'username': username, 'profile_pic': profile_pic_url, 'content': content}, broadcast=True)
    database.database.send(username, content)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=80, use_reloader=True, debug=True)
