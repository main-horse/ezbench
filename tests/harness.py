# NOT ACTUALLY A TEST DO NOT RUN ME
import dill
import functools
import time
import torch

from contextlib import contextmanager

def mp_worker(r: int, ws: int, f_bytes: bytes, prologue: callable, epilogue: callable):
    f = dill.loads(f_bytes)
    import os
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12345'
    os.environ['LOCAL_RANK'] = os.environ['RANK'] = str(r)
    os.environ['WORLD_SIZE'] = str(ws)
    torch.cuda.set_device(r)

    inp = prologue()
    res = f(*inp)
    epilogue(res)

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

def run_models_test(test, models=None):
    models = models or ["gpt-4o", "claude-3-7-sonnet-latest", "gemini-2.0-flash"]
    results = {}
    for model in models:
        print('='*100)
        print(f'Testing with {model}')
        print('='*100)
        from evaluator import run_test
        results[model] = run_test(test, llm_=model)
    
    return results

if __name__ == "__main__":
    assert ensure_nonblocking("lambda: 1")
    assert ensure_nonblocking("lambda: torch.zeros(1,device='cuda')")
    assert ensure_nonblocking("lambda: torch.randn(128,1024,1024,device='cuda')")
    def f(b=99,s=4096):
        with torch.device('cuda'): torch.randn(b,s)[torch.rand(b).le_(0.1).to(torch.bool)] = 0
    assert ensure_nonblocking(f)

    assert not ensure_nonblocking("torch.cuda.synchronize")
    assert not ensure_nonblocking("lambda: torch.tensor(1,device='cuda')")
    assert not ensure_nonblocking(lambda: (x:=torch.randn(128,device='cuda'), x[x!=0]))