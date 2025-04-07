import typing
import dill
from evaluator import *
from tests.harness import torch, extract_function, guarded, mp_worker

DESCRIPTION = """Can use init_device_mesh or DeviceMesh constructor to create a DeviceMesh.

Examples:
# [✅]
def create_mesh(dims: dict[str, int]):
    import torch
    return torch.distributed.device_mesh.init_device_mesh('cuda', list(dims.values()), mesh_dim_names=list(dims.keys()))
# [✅]
def create_mesh(dims: dict[str, int]):
    import math, torch
    return torch.distributed.device_mesh.DeviceMesh(
         device_type='cuda',
         mesh=torch.arange(math.prod(dims.values())).reshape(*dims.values()),
         mesh_dim_names = tuple(dims.keys()),
    )
[❌, misremembered kwarg (sonnet example)]
def create_mesh(dims: dict[str, int]):
    import os, torch
    import torch.distributed as dist
    if not dist.is_initialized(): dist.init_process_group("nccl")
    world_size = int(os.environ.get('WORLD_SIZE', '1'))
    dim_names = list(dims.keys())
    mesh_shape = [dims[name] for name in dim_names]
    device_mesh = torch.distributed.device_mesh.DeviceMesh(
        "cuda", torch.arange(world_size).reshape(mesh_shape), dim_names=dim_names
    )
[❌, hallucinated garbage (4o example)]
def create_mesh(dims: dict[str, int]):
    import os
    import torch
    import torch.distributed as dist
    from torch.distributed._tensor import DeviceMesh
    if not dist.is_initialized(): dist.init_process_group(backend='nccl')
    world_size = int(os.environ['WORLD_SIZE'])
    device_ids = list(range(world_size))
    mesh_shape = tuple(dims[key] for key in dims)  # Ensure order is maintained
    mesh_grid = torch.arange(world_size).reshape(*mesh_shape)
    device_mesh = DeviceMesh('cuda', mesh_grid.tolist())
    for dim, key in enumerate(dims): device_mesh.set_dimension_name(dim, key)
    return device_mesh
"""

question = """Implement `create_mesh(dims: dict[str, int]) -> torch.distributed.device_mesh.DeviceMesh`,
A function which initializes a (cuda) device mesh with the given dimensions (in dict order).

For example, create_mesh(dict(dp=2, tp=4)) should produce a DeviceMesh with:
* m.mesh == [[0,1,2,3],[4,5,6,7]]
* m['dp'].size() == 2 and m['tp'].size() == 4

You can assume that prod(dims.values()) == int(os.environ['WORLD_SIZE']),
that the function will be executed under a `torchrun`'d process.
Include all imports inline inside the function body.
"""

def mp_make_input() -> list: return [dict(dp=1, fs=2, cp=2, tp=2)]
def mp_check_output(mesh):
    assert isinstance(mesh, torch.distributed.device_mesh.DeviceMesh)
    assert mesh.device_type == 'cuda'
    assert hasattr(mesh, 'mesh') and isinstance(mesh.mesh, torch.Tensor)
    assert mesh.mesh.tolist() == [[[[0, 1], [2, 3]], [[4, 5], [6, 7]]]], mesh.mesh.tolist()
    
    assert hasattr(mesh, 'mesh_dim_names') and isinstance(mesh.mesh_dim_names, tuple)
    assert mesh.mesh_dim_names == ('dp', 'fs', 'cp', 'tp')

@guarded
def method_satisfies(f: typing.Callable[[dict[str, int]], torch.distributed.device_mesh.DeviceMesh], *, ws: int=8) -> bool:
    return torch.multiprocessing.spawn(
        mp_worker,
        args=(ws, dill.dumps(f), mp_make_input, mp_check_output),
        nprocs=ws,
        join=True
    ) is None


TestThing = question >> LLMRun() >> CorrectlyExtractCode() >> PyFunc(
    lambda s: method_satisfies(extract_function(s, 'create_mesh'))
)

if __name__ == "__main__":
    # codeblock = '''
    # def create_mesh(dims: dict[str, int]):
    #     import torch
    #     return torch.distributed.device_mesh.init_device_mesh('cuda', list(dims.values()), mesh_dim_names=list(dims.keys()))
    # '''
    # exec(codeblock, globals(), namespace := {})
    # print(method_satisfies(namespace['create_mesh']))
    # exit()

    from tests.harness import run_models_test
    run_models_test(TestThing)