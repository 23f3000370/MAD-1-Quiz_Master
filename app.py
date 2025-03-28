from flask import Flask, render_template
from controllers import register_blueprints

app = Flask(__name__)
app.secret_key = "23f3000370_secret_key"

register_blueprints(app)

@app.route("/")
def home():
    return render_template("auth/index.html")


if __name__ == "__main__":
    app.run(debug=True)
    



