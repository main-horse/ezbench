import typing
from evaluator import *
from tests.harness import torch, extract_function

DESCRIPTION = """Can use init_device_mesh or DeviceMesh constructor to create a DeviceMesh.

Examples:
# [✅]
def create_mesh(dims: dict[str, int]) -> torch.distributed.device_mesh.DeviceMesh:
    return torch.distributed.device_mesh.init_device_mesh('cuda', list(dims.values()), mesh_dim_names=list(dims.keys()))
# [✅]
def create_mesh(dims: dict[str, int]) -> torch.distributed.device_mesh.DeviceMesh:
    import math
    return torch.distributed.device_mesh.DeviceMesh(
         'cuda',
         torch.arange(math.prod(dims.values())).reshape(*dims.values()),
         mesh_dim_names = tuple(dims.keys()),
    )
[❌, wrong kwarg]
def create_mesh(dims: dict[str, int]) -> torch.distributed.device_mesh.DeviceMesh:
    import os
    import torch.distributed as dist
    if not dist.is_initialized(): dist.init_process_group("nccl")
    world_size = int(os.environ.get('WORLD_SIZE', '1'))
    dim_names = list(dims.keys())
    mesh_shape = [dims[name] for name in dim_names]
    device_mesh = torch.distributed.device_mesh.DeviceMesh(
        "cuda", torch.arange(world_size).reshape(mesh_shape), dim_names=dim_names
    )
"""



question = """Implement `create_mesh(dims: dict[str, int]) -> torch.distributed.device_mesh.DeviceMesh`,
A function which initializes a (cuda) device mesh with the given dimensions (in dict order).

For example, create_mesh(dict(dp=2, tp=4)) should produce a DeviceMesh with:
* m.mesh == [[0,1,2,3],[4,5,6,7]]
* m.mesh_dim_names == ['dp', 'tp']

You can assume that math.prod(dims.values()) == int(os.environ['WORLD_SIZE']),
that the function will be executed under a `torchrun`'d process,
and that `import torch` is already done.
"""

def _worker(rank: int, world_size: int, f: callable):
    import os
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12345'
    os.environ['LOCAL_RANK'] = os.environ['RANK'] = str(rank)
    os.environ['WORLD_SIZE'] = str(world_size)
    torch.cuda.set_device(rank)
    
    test_dims = dict(dp=1, fs=2, cp=2, tp=2)
    mesh = f(test_dims)
    assert isinstance(mesh, torch.distributed.device_mesh.DeviceMesh)
    assert mesh.device_type == 'cuda'
    assert hasattr(mesh, 'mesh') and isinstance(mesh.mesh, torch.Tensor)
    assert mesh.mesh.tolist() == [[[[0, 1], [2, 3]], [[4, 5], [6, 7]]]], mesh.mesh.tolist()
    
    assert hasattr(mesh, 'mesh_dim_names') and isinstance(mesh.mesh_dim_names, tuple)
    assert mesh.mesh_dim_names == ('dp', 'fs', 'cp', 'tp')
def method_satisfies(f: typing.Callable[[dict[str, int]], torch.distributed.device_mesh.DeviceMesh]) -> bool:
    try: return torch.multiprocessing.spawn(_worker, args=(8, f), nprocs=8, join=True) is None
    except: return __import__('traceback').print_exc() != None



TestThing = question >> LLMRun() >> CorrectlyExtractCode() >> PyFunc(
    lambda s: method_satisfies(extract_function(s))
)

if __name__ == "__main__":
    # print(method_satisfies(create_mesh))
    print(run_test(TestThing, llm_="gpt-4o"))
    # print(run_test(TestThing, llm_="claude-3-7-sonnet-latest"))
