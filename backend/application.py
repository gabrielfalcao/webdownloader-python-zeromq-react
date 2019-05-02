from flask import Flask, request
from flask import render_template

from backend.pushclient import PushClient


app = Flask(__name__)


remote_downloader = PushClient()


@app.route("/")
@app.route("/download")
def hello():
    return render_template('index.html')


@app.route("/download/push", methods=["POST"])
def push_download():
    url = request.form.get('url')
    remote_downloader.enqueue_url(url)
    return render_template('index.html', success=f"{url} will be enqueued in the next iteration")


if __name__ == '__main__':
    remote_downloader.connect()
    app.run(debug=True)
