from flask import Flask

from app import create_dash_application

app = Flask(__name__)

# base_url = '/dash/'
# testar passar como segundo parametro na função

create_dash_application(app)

if __name__ == "__main__":
    app.run()