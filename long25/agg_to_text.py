from evaluator import *

question = """
Create a Rust CLI program that takes an asciinema dump via stdin and outputs plain text dump of the terminal state each frame to stdout, using the same the frame choice algorithm that agg uses.  The output frame format is:

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

Note that lines are padded out to the full column length with spaces.

Use avt as your terminal emulator.  You will compile with the following Cargo.toml attached below.
I've also attached the agg source code as reference.
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

expect = """
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
----
Current Time: 2025-03-30 06:54:17   
╭────── 'log_view' (36 x 10) ──────╮
│                                  │
│                                  │
│                                  │
│     Layout(name='log_view')      │
│                                  │
│                                  │
│                                  │
│                                  │
╰──────────────────────────────────╯
----

Current Time: 2025-03-30 06:54:18   
╭────── 'log_view' (36 x 10) ──────╮
│                                  │
│                                  │
│                                  │
│     Layout(name='log_view')      │
│                                  │
│                                  │
│                                  │
│                                  │
╰──────────────────────────────────╯
----
Current Time: 2025-03-30 06:54:19   
╭────── 'log_view' (36 x 10) ──────╮
│                                  │
│                                  │
│                                  │
│     Layout(name='log_view')      │
│                                  │
│                                  │
│                                  │
│                                  │
╰──────────────────────────────────╯
----
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
----
"""

TestAggToText = (
    StringNode(question + cargo + context) >>
    MultiShotLLMRun(
        ExtractCode(keep_main=True) >> CargoRun(cargo, input=test_term),
    ) >>
    EqualEvaluator(expect)
)

if __name__ == "__main__":
    print(run_test(TestAggToText))
