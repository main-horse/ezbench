import functools
from evaluator import *
from tests.harness import ensure_nonblocking, torch

DESCRIPTION = """Ability to construct a dropout mask with arbitrary probability without blocking.

Examples:
[✅] nonblocking_mask_with_prob(size: int, prob: float): return torch.rand(size,device='cuda')<prob
[✅] nonblocking_mask_with_prob(s,p): return torch.empty(s,device='cuda').bernoulli_(p)
[❌, probability dist fake] def nonblocking_mask_with_prob(s,p): return torch.ones((s,),device='cuda',dtype=torch.bool)
[❌, wrong method argument] def nonblocking_mask_with_prob(s,p): return torch.full((s,),p,device='cuda').bernoulli_()
[❌, function name missing] lambda a,b: torch.rand(a,device='cuda')<b
"""

question = """Implement `nonblocking_mask_with_prob(size: int, p: float) -> torch.Tensor`,
A method which should create a boolean cuda tensor of shape `(size,)` with elements 0 or 1,
where each element is 1 with probability `p` and 0 otherwise.

The method **should not block/synchronize** the CPU for any GPU work to complete. That is,
* no H2D/D2H transfers
* no implicit/explicit syncs
* must launch nonblocking cuda work only
Assume torch is already imported.
"""

def method_satisfies(f: callable) -> bool:
    try: t = f()
    except: return __import__('traceback').print_exc() != None # always False
    likeness = t.device.type == 'cuda' and t.numel() == 1<<16 and t.ndim == 1 and t.dtype == torch.bool
    percentage = t.nonzero().numel() / t.numel()
    return likeness and abs(percentage - 0.1) < 0.05

def extract_function(code_str: str) -> callable:
    namespace = {}
    exec(code_str, globals(), namespace)
    return namespace.get('nonblocking_mask_with_prob')


TestThing = question >> LLMRun() >> CorrectlyExtractCode() >> PyFunc(lambda s: functools.partial(extract_function(s), 1<<16, 0.1)) >> AndNode(
    PyFunc(ensure_nonblocking), # check that it's nonblocking,
    PyFunc(method_satisfies) # check that it satisfies the method's contract
)

if __name__ == "__main__":
    # print(run_test(TestThing, llm_="gpt-4o"))
    print(run_test(TestThing, llm_="claude-3-7-sonnet-latest"))
