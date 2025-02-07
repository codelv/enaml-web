import sys
import time
import tracemalloc
import linecache
import pytest
from subprocess import Popen, PIPE, STDOUT
from textwrap import dedent
from conftest import compile_source

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


def diff_stats(snapshot1, snapshot2, label: str, limit: int = 20):
    top_stats = snapshot2.compare_to(snapshot1, "lineno")

    print(f"------- Top {limit} differences {label} -------")
    for stat in top_stats[:limit]:
        print(stat)


def display_top(snapshot, key_type="lineno", limit=20):
    snapshot = snapshot.filter_traces(
        (
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        )
    )
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        print(
            "#%s: %s:%s: %.1f KiB (%i)"
            % (index, frame.filename, frame.lineno, stat.size / 1024, stat.count)
        )
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print("    %s" % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


def snap_and_show_stats(snapshots, label):
    snapshots.append(tracemalloc.take_snapshot())
    display_top(snapshots[-1])
    diff_stats(snapshots[-2], snapshots[-1], "after construct")


@pytest.fixture
def tmalloc():
    tracemalloc.start()
    try:
        yield
    finally:
        tracemalloc.stop()


def test_html_size(tmalloc, app):
    Page = compile_source(
        dedent(
            """
    from web.components.api import *
    from web.core.api import *
    enamldef Page(Html): view:
        Head:
            Title:
                text = "Table"
        Body:
            Table:
                TBody:
                    Looper:
                        iterable = range(1000)
                        Tr:
                            Td:
                                text = f"{loop.index}"
                            Looper:
                                iterable = range(99)
                                Td:
                                    text = f"{loop.item}"

    """
        ),
        "Page",
    )
    snapshots = []
    snapshots.append(tracemalloc.take_snapshot())
    display_top(snapshots[-1])

    t0 = time.time()
    view = Page()

    print(f"\n\n\nConstruct took {time.time()-t0}")
    snap_and_show_stats(snapshots, "after construct")

    t0 = time.time()
    view.initialize()
    print(f"\n\n\nInit took {time.time()-t0}")
    snap_and_show_stats(snapshots, "after init")

    t0 = time.time()
    view.activate_proxy()
    print(f"\n\n\nActivate took {time.time()-t0}")
    snap_and_show_stats(snapshots, "after activate")

    t0 = time.time()
    content = view.render()
    print(f"\n\n\nRender took {time.time()-t0}")
    snap_and_show_stats(snapshots, "after render")

    total_size = 0
    num_nodes = 0
    for node in view.traverse():
        num_nodes += 1
        total_size += sys.getsizeof(node)
    assert total_size < 5_000_000
    assert len(content) < 2_500_000
    assert False


if __name__ == "__main__":
    test_mem_usage()
