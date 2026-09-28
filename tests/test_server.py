import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest
from tonecar.server import Handler, regression


@pytest.fixture
def local_server():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown(); server.server_close(); thread.join()


def test_health_and_no_private_files(local_server):
    assert json.load(urlopen(local_server+'/api/health'))['status'] == 'ok'
    for path in ['/.env', '/tonecar/server.py', '/download?file=../../.env']:
        with pytest.raises(HTTPError) as exc:
            urlopen(local_server+path)
        assert exc.value.code == 404


def test_filtered_regression_does_not_claim_small_sample():
    result = regression({'ticker':['AAPL'], 'year':['2025']})
    assert not result['available']
    assert result['n'] < 8


def test_invalid_query_is_rejected(local_server):
    with pytest.raises(HTTPError) as exc:
        urlopen(local_server+'/api/regression?alignment=../../.env')
    assert exc.value.code == 400


def test_real_regression_returns_confidence_interval():
    result = regression({})
    assert result['available']
    term = next(row for row in result['rows'] if row['term'] == 'tone')
    assert term['low'] < term['coefficient'] < term['high']
