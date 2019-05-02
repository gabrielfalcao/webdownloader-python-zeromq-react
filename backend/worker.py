import hashlib
import requests
import logging
import threading
import zmq
import coloredlogs

logger = logging.getLogger(__name__)


def download_url(url, progress_callback):
    # filename will be the sha1 of url
    filename = hashlib.sha1(url.encode('utf-8')).hexdigest()
    with open(filename, "wb") as fd:
        response = requests.get(url, stream=True)
        total = response.headers.get("content-length")

        if total is None:
            fd.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            ideal_chunk_size = min(int(total / 1024), 1024 * 1024)
            for data in response.iter_content(
                chunk_size=ideal_chunk_size
            ):
                downloaded += len(data)
                fd.write(data)

                try:
                    progress_callback(url, downloaded, total)
                except Exception as err:
                    logger.warning(f"failed to call {progress_callback} with url {url}, downloaded {downloaded}, total {total}: {err}")


class BackgrounDownloader:
    def __init__(self, bind_address='tcp://127.0.0.1:4242'):
        self.ctx = zmq.Context()
        self.lock = None
        self.thread = None
        self.address = bind_address

    def loop_once(self):
        logger.info('waiting for job...')
        url = self.jobs.recv_string()
        # TODO: sanitize malicious urls
        download_url(url, lambda url, downloaded, total: print(f'progress for {url}:\t{downloaded}/{total}'))

    def serve_forever(self):
        # create socket inside thread
        logger.debug('creating PULL socket...')
        self.jobs = self.ctx.socket(zmq.PULL)
        logger.info(f'binding server to {self.address}...')
        self.jobs.bind(self.address)
        logger.debug('acquiring lock...')
        while self.lock.acquire():
            self.loop_once()
            logger.debug('releasing lock...')
            self.lock.release()

    def start(self):
        if self.lock is not None:
            raise RuntimeError('cannot .start() {self} because a lock is already set')

        if self.thread is not None:
            raise RuntimeError('cannot .start() {self} because a thread already exists')

        self.lock = threading.RLock()
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.start()

    def stop(self):
        try:
            logger.info(f'waiting for thread to finish job and release lock')
            self.lock.acquire()
        except KeyboardInterrupt:
            self.thread.cancel()
            logger.warning(f'thread {self.thread} was abruptly cancelled by user')


if __name__ == '__main__':
    coloredlogs.install(level='DEBUG')
    worker = BackgrounDownloader()
    worker.start()
