from flask import Flask, jsonify
import scraper

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/<path:url>', methods=['GET'])
def get_response(url):
    return jsonify(scraper.main(url))


if __name__ == '__main__':
    app.run()
