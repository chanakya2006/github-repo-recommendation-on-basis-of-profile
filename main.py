from flask import Flask, jsonify, render_template, request
from ClassfileforGitHubRecommendation import *
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# API Endpoint with Parameter
@app.route('/api')
def get_data():
    name = request.args.get("name"," ")
    response = {}
    p = GitHubProjectRecommender().get_recommendations_for_user(name)
    print(p)
    for i in range(len(p)):
        response[i] = {"repo_name": p[i]["url"].split("/")[-1], "url" : p[i]["url"], "Description" : p[i]["description"]}
    # for i in range(5):
    #     response[i] = {"repo_name" : name, "url" : f"https://github.com/{name}", "Description" : "Hello there !!"}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)