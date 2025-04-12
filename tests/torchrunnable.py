from evaluator import *

DESCRIPTION = """Check default model behavior: does it
1. know "torchrun" = SPMD script?
2. know to init distributed?
3. do cuda.set_device?

Examples:
[✅] 
import torch
import torch.distributed as dist
dist.init_process_group(backend='nccl')
torch.cuda.set_device(dist.get_rank())
t = torch.randn(8, device='cuda')
dist.all_reduce(t, op=dist.ReduceOp.SUM)
[❌, obviously not torchrunnable] 
def main():
    world_size = 4  # Number of processes/nodes
    mp.spawn(run_allreduce, args=(world_size,), nprocs=world_size, join=True)
[❌, creates cuda:0 tensor on all ranks] 
import torch
import torch.distributed as dist
dist.init_process_group()
t = torch.ones(10, dtype=torch.float32, device='cuda')
dist.all_reduce(t, op=dist.ReduceOp.SUM)
"""

question = """Create a torchrunnable script that runs allreduce on a cuda tensor."""

# NOTE: we don't actually run anything, we just string match for some common sense requirements
# this is obviously easy to cheat if you're a human reading the checker.
# for an llm that never sees it i think it's fine
predicates = [
    OrNode(SubstringEvaluator("allreduce"), SubstringEvaluator("all_reduce")),
    SubstringEvaluator("init_process_group"),
    SubstringEvaluator("set_device"),
    NotNode(SubstringEvaluator("multiprocessing")),
    NotNode(SubstringEvaluator("mp.spawn")),
]
def RequireAll(p: list[Node]) -> Node:
    match len(p):
        case 0: raise RuntimeError
        case 1: return p[0]
        case _: return AndNode(p[0], RequireAll(p[1:]))

TestThing = question >> LLMRun() >> CorrectlyExtractCode() >> RequireAll(predicates)

if __name__ == "__main__":
    from tests.harness import run_models_test
    run_models_test(TestThing)
