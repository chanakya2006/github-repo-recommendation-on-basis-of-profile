from flask import Flask, jsonify, render_template, request
from Content_based_Rec import GitHubRecommender
from flask_cors import CORS

# To run : python main.py

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

# API Endpoint with Parameter
@app.route('/api')
def get_data():
    name = request.args.get("name"," ")
    response = {}
    p = GitHubRecommender().get_recommendations_for_user(name)
    print(p)
    for k,i in enumerate(p):
        print(i)
        response[k] = {"repo_name": "/".join(i.split("/")[len(i.split("/"))-2:len(i.split("/"))]), "url" : i, "Description": ""}#"Description" : p[i]}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=False)