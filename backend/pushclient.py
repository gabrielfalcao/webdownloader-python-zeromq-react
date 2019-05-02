import zmq


class PushClient:
    def __init__(self, address=f'tcp://127.0.0.1:4242'):
        self.ctx = zmq.Context()
        self.push = self.ctx.socket(zmq.PUSH)
        self.address = address

    def connect(self):
        self.push.connect(self.address)

    def enqueue_url(self, url):
        self.push.send_string(url)


if __name__ == '__main__':
    client = PushClient()
    client.connect()
    client.enqueue_url('https://github.com/gabrielfalcao/HTTPretty/raw/master/docs/source/_static/logo.svg?sanitize=true')
