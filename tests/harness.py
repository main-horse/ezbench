# NOT ACTUALLY A TEST DO NOT RUN ME
import functools
import time
import torch

from contextlib import contextmanager

def extract_function(code_str: str, fn_name: str) -> callable:
    namespace = {}
    exec(code_str, globals(), namespace)
    return namespace.get(fn_name)

@contextmanager
def timeit():
    start_time = time.time()
    ptr = []
    try: yield lambda: ptr.pop() - start_time
    finally: ptr.append(time.time())

def guarded(f):
    @functools.wraps(f)
    def inner(*a,**k):
        try: return f(*a,**k)
        except: return __import__('traceback').print_exc() != None
    return inner

@guarded
def ensure_nonblocking(code: "str | Callable[[], Any]") -> bool:
    def huge_nonblocking_work(
        a=torch.randn(50,4096,4096,device='cuda'),
        o=torch.empty(50,4096,4096,device='cuda')
    ): return torch.bmm(a,a,out=o)
    f = eval(code) if isinstance(code, str) else code
    # ensure kernels, cuda alloc, etc. all exist
    huge_nonblocking_work() 
    f()
    #
    torch.cuda.synchronize()
    with timeit() as outer:
        with timeit() as inner:
            huge_nonblocking_work()
            f()
        torch.cuda.synchronize()
    # heuristic: we expect the cpu exec time to be at least 5x faster than the gpu
    inner,outer = inner(),outer()
    return inner*5 < outer

if __name__ == "__main__":
    assert ensure_nonblocking("lambda: 1")
    assert ensure_nonblocking("lambda: torch.zeros(1,device='cuda')")
    assert ensure_nonblocking("lambda: torch.randn(128,1024,1024,device='cuda')")
    assert ensure_nonblocking("lambda: torch.empty(65536,device='cuda').bernoulli_(0.01)")