import time
import os
import importlib
import multiprocessing
import queue
import logging
import logging.handlers
from pytest import mark, fixture
from crds.core import config, log
from crds.sync import SyncScript
from crds.core.heavy_client import getreferences
from crds.core.cache_locker import crds_lock
log.THE_LOGGER.logger.propagate = True
log.set_verbose(40)


### Dynamic Fixtures for multiprocessing lock tests ###

@fixture(autouse=False, name="mp_lock_manager")
def mp_lock_manager():
    """Clean isolation of multiprocessing manager lifetime per test. Forces shutdown of any stale managers from previous tests, initializes a fresh manager for each specifc test execution, and cleans up immediately after the test completes to avoid leaking state into subsequent tests."""
    from crds.core.cache_locker import shutdown_mp_manager, initialize_multiprocessing_mode
    shutdown_mp_manager()
    initialize_multiprocessing_mode() # ACTIVATE MP MUX
    yield
    shutdown_mp_manager()

### multiprocessing.Process lock tests ###

def parallel_worker_task(payload):
    """Target function executed by independent worker processes. Accepts and binds the shared proxy state `shared_dict` for strict spawn-based environments (i.e. github actions CI/CD).
    payload format:
    (worker_id: int, target_path: str, output_queue: multiprocessing.Queue, shared_dict=None, 
    func: callable, func_args: tuple, func_kwargs: dict)
    """
    worker_id, target_path, output_queue, shared_dict = payload
    if shared_dict is not None:
        from crds.core.cache_locker import initialize_multiprocessing_mode
        initialize_multiprocessing_mode(shared_dict=shared_dict)
    try:
        with crds_lock(target_path, timeout=10.0):
            start_time = time.time()
            time.sleep(0.5)  # Simulate work being done while holding the lock
            end_time = time.time()
            output_queue.put({
                "worker_id": worker_id,
                "start": start_time,
                "end": end_time,
                "success": True
            })
    except Exception as e:
        output_queue.put({"worker_id": worker_id, "success": False, "error": str(e)})


@mark.skip(reason="Skipping due to intermittent failures in CI/CD. Needs investigation.")
@mark.multimission
@mark.locking
def test_multiprocessing_locking(mp_lock_manager, tmp_path):
    local_target = str(tmp_path / "test_mp_lock.tmp")
    from crds.core.cache_locker import _MULTIPROCESSING_LOCKS
    ctx = multiprocessing.get_context()
    result_queue = ctx.Queue()
    workers = []
    num_workers = 3
    for i in range(3):
        payload = (i, local_target, result_queue, _MULTIPROCESSING_LOCKS)
        p = ctx.Process(
            target=parallel_worker_task, 
            args=(payload,)
        )
        workers.append(p)
        p.start()
    for p in workers:
        p.join()
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    # checks
    assert len(results) == num_workers
    results.sort(key=lambda x: x["start"])
    for i in range(1, len(results)):
        previous_worker_end = results[i-1]["end"]
        current_worker_start = results[i]["start"]
        assert current_worker_start >= previous_worker_end, (
            f"Lock Failure: Worker {results[i]['worker_id']} entered at {current_worker_start:.2f} "
            f"before the previous worker left at {previous_worker_end:.2f}."
        )

### multiprocessing.Pool lock tests ###

def pool_worker_task(payload):
    """
    A reusable, generic worker task for multiprocessing pool tests.
    
    Payload format:
        (worker_id, target_lock_path, target_func, func_args, func_kwargs)
    """
    worker_id, target_path = payload
    try:
        with crds_lock(target_path, timeout=10.0):
            start_time = time.time()
            time.sleep(0.5)  # Simulate work being done while holding the lock
            end_time = time.time()
            return {
                "worker_id": worker_id,
                "start": start_time,
                "end": end_time,
                "success": True
            }
    except Exception as e:
        return {"worker_id": worker_id, "success": False, "error": str(e)}


@mark.skip(reason="Skipping due to intermittent failures in CI/CD.")
@mark.locking
def test_pool_locking_generic(mp_lock_manager, tmp_path):
    local_target = str(tmp_path / "test_pool_cache_file.tmp")
    num_workers = 3
    import crds.core.cache_locker as cache_locker
    cache_locker.shutdown_mp_manager()  # Ensure no stale managers are running
    ctx = multiprocessing.get_context()
    task_payload = [(i, local_target) for i in range(num_workers)]
    with ctx.Pool(
        processes=num_workers,
        initializer=cache_locker.initialize_multiprocessing_mode,
        initargs=(cache_locker._MULTIPROCESSING_LOCKS,) # force single-item tuple
    ) as pool:
        # map() blocks until all workers return their results
        results = pool.map(pool_worker_task, task_payload)
    assert len(results) == num_workers
    results.sort(key=lambda x: x["start"])
    for i in range(1, len(results)):
        previous_worker_end = results[i-1]["end"]
        current_worker_start = results[i]["start"]
        assert current_worker_start >= previous_worker_end, (
            f"Lock Failure in Pool! Worker {results[i]['worker_id']} entered at {current_worker_start:.2f} "
            f"before the previous worker left at {previous_worker_end:.2f}."
        )


class LogCaptureHandler(logging.handlers.BufferingHandler):
    """Lightweight buffering handler to capture records inside a pool worker."""
    def __init__(self):
        super().__init__(capacity=1000)

def pool_getrefs_worker(payload):
    """Worker function for testing getreferences with multiprocessing locks."""
    worker_id, header, reftypes, context, observatory = payload
    log.set_verbose(40)
    capture_handler = LogCaptureHandler()
    log.THE_LOGGER.logger.addHandler(capture_handler)
    try:
        getreferences(parameters=header, reftypes=reftypes, context=context, observatory=observatory)
        worker_logs = [
            {"created": rec.created, "message": rec.getMessage()}
            for rec in capture_handler.buffer
            if "multiprocessing lock for roman_wfi_abvegaoffset_0010.asdf" in rec.getMessage()
        ]
        return {"worker_id": worker_id, "logs": worker_logs, "success": True}
    except Exception as e:
        return {"worker_id": worker_id, "success": False, "error": str(e)}
    finally:
        log.THE_LOGGER.logger.removeHandler(capture_handler) # clean up to avoid memory pollution


@mark.skip(reason="Skipping due to intermittent failures in CI/CD. Needs investigation.")
@mark.locking
def test_pool_locking_getreferences(mp_lock_manager, roman_temp_cache_state):
    """
    Integration test validating that getreferences acts sequentially
    when mapped concurrently across multiple workers.
    """
    import crds.core.cache_locker as cache_locker
    shared_dict = cache_locker._MULTIPROCESSING_LOCKS
    header = {
        'ROMAN.META.INSTRUMENT.NAME': 'wfi',
        'ROMAN.META.EXPOSURE.START_TIME': '2026-01-01',
        'ROMAN.META.INSTRUMENT.DETECTOR': 'WFI01',
    }
    num_workers = 3    
    task_payloads= [(i, header, ['abvegaoffset'], "roman_0061.pmap", "roman") for i in range(num_workers)]
    ctx = multiprocessing.get_context()
    with ctx.Pool(
        processes=num_workers,
        initializer=cache_locker.initialize_multiprocessing_mode,
        initargs=(shared_dict,)
    ) as pool:
        results = pool.map(pool_getrefs_worker, task_payloads)
    all_lock_events = []
    for r in results:
        assert r["success"] is True, f"Worker {r['worker_id']} crashed: {r.get('error')}"
        all_lock_events.extend(r["logs"])
    all_lock_events.sort(key=lambda x: x["created"])
    for ev in all_lock_events:
        print(f"[{ev['created']:.4f}] {ev['message']}")
    assert len(all_lock_events) > 0, "No lock events were captured from any worker."
    for i in range(len(all_lock_events)):
        msg = all_lock_events[i]["message"]
        if i % 2 == 0:
            assert "Acquired" in msg, f"Expected lock acquisition at step {i}, but got: {msg}"
        else:
            assert "Released" in msg, f"Expected lock release at step {i}, but got: {msg}"
    ref = os.path.join(roman_temp_cache_state.cache, "references/roman/roman_wfi_abvegaoffset_0010.asdf")
    assert os.path.exists(ref), f"Expected file not found in cache at: {ref}"


### Integrated file lock tests ###

@mark.locking
def test_sync_filelock(hst_temp_cache_state, caplog):
    log.set_verbose(40)
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        status = SyncScript("crds.sync --contexts hst_0006.pmap")()
        out = caplog.text
    assert "Acquired file lock" in out, "Expected file lock acquisition log not found."
    assert "Released file lock" in out, "Expected file lock release log not found."
    assert status == 0


@mark.locking
def test_getrefs_filelock(jwst_shared_cache_state, caplog):
    log.set_verbose(40)
    header = {
        "META.INSTRUMENT.NAME":"MIRI",
        "META.EXPOSURE.TYPE":"MIR_IMAGE",
        "META.OBSERVATION.DATE":"2018-05-25",
        "META.OBSERVATION.TIME":"00:00:00"
    }
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        refs = getreferences(
            header,
            observatory="jwst",
            context="jwst_miri.imap",
            ignore_cache=True,
            reftypes=["flat"]
        )
        out = caplog.text
    assert "Acquired file lock" in out, "Expected file lock acquisition log not found."
    assert "Released file lock" in out, "Expected file lock release log not found."
    cache_path = jwst_shared_cache_state.cache
    assert refs == {'flat': f'{cache_path}/references/jwst/jwst_miri_flat_0001.fits'}



@mark.locking
def test_default_readonly(default_shared_state, caplog):
    config.set_cache_readonly()
    log.set_verbose(40)
    assert config.lock_status() == "disabled"
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        status = SyncScript("crds.sync --contexts hst_0006.pmap")()
        out = caplog.text
    expected_out = "Syncing READONLY cache,  only checking functions are enabled."
    assert expected_out in out
    assert "Acquired file lock" not in out, "Unexpected file lock acquisition log found in read-only mode."
    assert status == 0
