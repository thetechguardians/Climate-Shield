# intentionally left empty — makes backend a package for making
# it as importable from the outside

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

#  Restrict CORS to your deployed frontend domain
CORS(app, resources={
    r"/api/*": {"origins": "https://your-frontend.example.com"}
})
