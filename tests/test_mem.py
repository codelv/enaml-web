import time
import pytest
from subprocess import Popen, PIPE, STDOUT

try:
    import requests
    import psutil
    import tornado  # noqa: F401

    DEPS_UNAVAILABLE = False
except ImportError as e:
    DEPS_UNAVAILABLE = True
    print(e)


@pytest.mark.skipif(DEPS_UNAVAILABLE, reason="Requires requests and psutil")
def test_mem_usage():
    """Tests that memory usage tapers off and does not keep increasing"""
    cmd = ["python", "examples/simple_site/main.py"]
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    url = "http://localhost:8888"
    try:
        time.sleep(0.2)
        total = 20000
        half = int(total / 2)
        p = psutil.Process(proc.pid)
        n = 0
        half_mem_info = None
        for i in range(total):
            r = requests.get(url)
            assert r.ok
            if n == 1000:
                n = 0
                mem_info = p.memory_info()
                if half_mem_info is None and i >= half:
                    half_mem_info = mem_info
                print(f"{round(i*100/total)}% - {mem_info}")
            n += 1
        assert (
            half_mem_info == mem_info
        ), "ERROR: Memory leak detected\nhalf={}\nfinal={}".format(
            half_mem_info, mem_info
        )
        print("OK!")
    except KeyboardInterrupt:
        print("Aborted")
    finally:
        proc.kill()
        print(proc.stdout.read())


if __name__ == "__main__":
    test_mem_usage()
