from evaluator import *

EASY_MODE = False

DESCRIPTION = """Knows F.linear(a,b) is a@b.mT, not a@b

Examples:
[✅] B
[❌] A
"""

question = f"""For the following question, respond solely with `A` or `B`, no other tokens.

Which value is {'torch.nn.functional' if EASY_MODE else 'F'}.linear(x,y) closest to?

[A] x@y
[B] x@y.mT

Answer:"""


TestThing = question >> LLMRun() >> SubstringEvaluator("B", lower=True)

if __name__ == "__main__":
    from tests.harness import run_models_test
    run_models_test(TestThing)

