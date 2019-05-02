import hashlib
import requests
import logging


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


if __name__ == '__main__':
    download_url('https://github.com/gabrielfalcao/HTTPretty/raw/master/docs/source/_static/logo.svg?sanitize=true', print)
