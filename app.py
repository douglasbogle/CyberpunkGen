import os
from config import Config
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Video
from generate import TitleGenerator


app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = '09e5f4161b84302a5dfa0fc29338cff8'
db.init_app(app)


@app.route("/", methods=['GET', 'POST'])
@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        prompt = request.form['prompt']
        temperature = float(request.form['temperature'])
        top_k = int(request.form['top_k'])
        top_p = float(request.form['top_p'])
        # Grab the users selected prompt and parameters!

        generator = TitleGenerator()
        fine_tuned_titles, pretrained_titles = generator.gen_titles(prompt, temperature, top_k, top_p)

        return render_template('generate.html', fine_tuned_titles=fine_tuned_titles, pretrained_titles=pretrained_titles)  # Pass to generate.html for formatting

    return render_template('generate.html')


'''@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400'''


if __name__ == '__main__':
    app.run(debug=True)








