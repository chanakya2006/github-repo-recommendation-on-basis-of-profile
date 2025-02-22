from flask import Flask, jsonify, render_template, request
from Content_based_Rec import GitHubRecommender


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# API Endpoint with Parameter
@app.route('/api')
def get_data():
    name = request.args.get("name"," ")
    if name == "123":
        response = {}
        for i in range(10):
            print(i)
            response[i] = {"repo_name" : f"jai/mata/di{i}", "url" : "https://github.com/chanakya2006", "Description" : "jSHBfvouySHVubzdfiuyvgdzuyfbvuzdgfvuhdbfvouydbuydzbiuygbdubdufgbhsdbgfubbuyghbudgbuzdguzdhfboiuzdtobiutuby"}
        return jsonify(response)
    response = {}
    p = GitHubRecommender(webdriver_path="D:\webdriver\chromedriver-win64\chromedriver.exe").get_recommendations_for_user(name)
    print(p)
    for k,i in enumerate(p):
        response[k] = {"repo_name": "/".join(i.split("/")[-3:-1]), "url" : i, "Description" : p[i]}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)