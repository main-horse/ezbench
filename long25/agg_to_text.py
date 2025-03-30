from evaluator import *

question = """
Create a Rust CLI program that takes an asciinema dump via stdin and outputs plain text dump of the terminal state each frame to stdout.  You must use the SAME frame choice algorithm that agg uses (it's source code will be attached later).

The output frame format should be as follows:

```
FRAME0_LINE0 (COL characters wide)
FRAME0_LINE1
...
FRAME0_LINEN (ROW characters tall)
----
FRAME1_LINE0
...
---- (trailing delimiter)
```

For example, suppose an asciinema dump is of a 2x2 window counting down from three.  Then we output:

```
3 
  
----
2 
  
----
1 
  
----
0 
  
----
```

Use avt as your terminal emulator.

You will compile with the following Cargo.toml attached below; do not use any
other dependencies.  After the Cargo.toml is the complete source code of agg,
which you should use as reference.

"""

extra_prompt = """
Use the same frame selection algorithm as agg:
- Batching events based on timing and FPS cap
- Accelerating playback based on speed parameter
- Limiting idle time between frames

Use the default settings for these parameters:
- Idle time limit (5.0 seconds)
- Playback speed (1.0)
- FPS cap (30)
"""

cargo = r"""
[package]
name = "agg_to_text"
version = "0.1.0"
edition = "2024"

[dependencies]
avt = "0.15.1"
anyhow = "1.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

"""

context = read_file(__file__, 'agg_to_text.context.md').decode()
test_term = read_file(__file__, 'agg_to_text.test.term')
expect = read_file(__file__, 'agg_to_text.expect.txt').decode()

TestAggToText = (
    StringNode(question + cargo + context) >>
    MultiShotLLMRun(
        ExtractLongestCode() >> CargoRun(cargo, input=test_term),
        max_iters=5,
    ) >>
    EqualEvaluator(expect)
)

if __name__ == "__main__":
    print(run_test(TestAggToText))
