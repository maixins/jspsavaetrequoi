import random
from flask import Flask, render_template, request



app = Flask(__name__)
app.config["SECRET_KEY"] = 'adfqsgERUEFB'


class message:
    compteur = 0
    def __init__(self):
        message.compteur += 1
        self.isread = message.r_status()
        self.message = "Bonsoir j'adore les framboisess"



        self.link = f"https://kitt.lewagon.com/placeholder/users/random?{message.compteur}"

    @staticmethod
    def r_status():
        r = random.randint(0,1)
        if r:
            return "unread"
        else:
            return "read"

message_list = [message(),message(),message(),message(),message()]*3

@app.route("/", methods=["GET"])
def index():
    print(request.remote_addr)
    return render_template('index.html', ids=message_list)



@app.route('/search', methods=['POST'])
def search():
    query = request.form['search']
    return f"{query}"


@app.route('/upload', methods=['POST','GET'])
def upload():
    if 'file' not in request.files:
        return 'No file found'

    file = request.files['file']

    if file.filename == '':
        return 'No file selected'

    file.save(f"database/temp-img/{file.filename}")
    return 'File uploaded successfully'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80,use_reloader=True,debug=True)