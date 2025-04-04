from evaluator import *

DESCRIPTION = "Without prompting, model should use modern, portable practices to implement nontrivial stdin multiplexing."

question = "Write a Python program using standard library only that prints the current time every second, but pauses if the user presses 'p' on the keyboard (no newline)."

TestStdinPause = StringNode(question) >> LLMRun() >> ExtractCode() >> NotNode(RegexEvaluator(r'fcntl|set_blocking|O_NONBLOCK'))

if __name__ == "__main__":
    print(run_test(TestStdinPause))
