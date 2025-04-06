# NOT ACTUALLY A TEST DO NOT RUN ME
import time
import torch

from contextlib import contextmanager

@contextmanager
def timeit():
    start_time = time.time()
    ptr = []
    try: yield lambda: ptr.pop() - start_time
    finally: ptr.append(time.time())

def huge_nonblocking_work(
    a=torch.randn(100,4096,4096,device='cuda'),
    o=torch.empty(100,4096,4096,device='cuda')
): return torch.bmm(a,a,out=o)

def ensure_nonblocking(code: str) -> bool:
    f = eval(code)
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
    return inner()*5 < outer()

if __name__ == "__main__":
    assert ensure_nonblocking("lambda: 1")
    assert ensure_nonblocking("lambda: torch.zeros(1,device='cuda')")
    assert ensure_nonblocking("lambda: torch.randn(128,1024,1024,device='cuda')")