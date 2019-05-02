from flask import Flask, request
from flask import render_template

app = Flask(__name__)


@app.route("/")
@app.route("/download")
def hello():
    return render_template('index.html')


@app.route("/download/push", methods=["POST"])
def push_download():
    url = request.form.get('url')
    return render_template('index.html', success=f"{url} will be enqueued in the next iteration")


if __name__ == '__main__':
    app.run(debug=True)
