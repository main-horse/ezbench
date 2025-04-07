import typing
import dill
from evaluator import *
from tests.harness import torch, extract_function, guarded, mp_worker

EASY_MODE = True # even this doesn't help :/

DESCRIPTION = """Is aware of recent default backend changes to init_process_group

Examples:
[✅] torch.distributed.init_process_group('cpu:gloo,cuda:nccl')
[❌] torch.distributed.init_process_group()
"""

question = """Provide a single expression to initialize the default torch distributed process group,
such that **both** CPU and GPU tensors will work with torch.distributed collectives after running it once.

You can assume that,
1. torch is imported & in the global namespace,
2. the expression will be executed under a `torchrun`'d process.
"""
if EASY_MODE: question += "\nTo be clear: "\
    "it must be the case that dist.all_reduce(t_cpu) and dist.all_reduce(t_gpu) " \
    "BOTH work during a SINGLE torchrun session."

def mp_make_input(): return []
def mp_check_output(_):
    import torch
    import torch.distributed as dist
    import torch.distributed._functional_collectives as funcol
    assert dist.is_initialized()

    t_local_cpu = torch.full((1,),dist.get_rank())
    t_local_gpu = t_local_cpu.cuda()
    t_world_cpu = funcol.all_gather_tensor(t_local_cpu, 0, group=dist.group.WORLD).wait()
    t_world_gpu = funcol.all_gather_tensor(t_local_gpu, 0, group=dist.group.WORLD).wait()
    assert t_world_cpu.tolist() == t_world_gpu.tolist() == [i for i in range(dist.get_world_size())]

def construct_function(expr: str) -> typing.Callable[[], None]:
    code = f'def f(torch=__import__("torch")): {expr.strip()}'
    return extract_function(code, 'f')

@guarded
def method_satisfies(f: typing.Callable[[], None], *, ws: int=2) -> bool:
    return torch.multiprocessing.spawn(
        mp_worker,
        args=(ws, dill.dumps(f), mp_make_input, mp_check_output),
        nprocs=ws,
        join=True
    ) is None

TestThing = question >> LLMRun() >> CorrectlyExtractCode() >> PyFunc(
    lambda s: method_satisfies(construct_function(s))
)
