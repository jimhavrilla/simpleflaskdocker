from flask import Flask
from elastic.query import elasticquery
import os

app = Flask(__name__)

@app.route("/")
def hello():
    try:
        result = elasticquery("Abdominal","sample")
        return result
    except Exception as e:
        print (e)
        return "Hello world!"

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, port=5004)
