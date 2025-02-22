from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# API Endpoint with Parameter
@app.route('/api')
def get_data():
    name = request.args.get("name"," ")
    response = {}
    for i in range(5):
        response[i] = {"repo_name" : name, "url" : f"https://github.com/{name}", "discription" : "Hello there !!"}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)