from evaluator import *
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from harness import ensure_nonblocking, torch

DESCRIPTION = """Basic awareness of implicit H2D transfers.

Examples:
[❌] torch.tensor(0).cuda()
[❌] torch.tensor(0, device='cuda')
[❌] torch.zeros(1, device='cuda')
[✅] torch.zeros(1, device='cuda')[0]
"""

question = "Provide a single expression to create a scalar (0-dim) cuda pytorch tensor with value 0, " \
"done in a way that will not trigger a blocking wait / syncronization.\n" \
"Assume torch is already imported."

def tensor_satisfies(t: torch.Tensor) -> bool:
    return t.device.type == 'cuda' and t.ndim == 0 and t.item() == 0

TestThing = question >> LLMRun() >> CorrectlyExtractCode() >> AndNode(
    PyFunc(lambda s: ensure_nonblocking(f"lambda: {s.strip()}")), # check that it's nonblocking,
    PyFunc(lambda s: tensor_satisfies(eval(s))) # check that it's a scalar cuda tensor with value 0
)

if __name__ == "__main__":
    from tests.harness import run_models_test
    run_models_test(TestThing)
