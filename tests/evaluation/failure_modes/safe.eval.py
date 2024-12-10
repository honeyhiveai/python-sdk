from honeyhive import evaluator, evaluate

import random
import time

@evaluator
def mean(results):
    return sum(results) / len(results)

@evaluator(
    asserts=False, 
    repeat=5,
    aggregate='mean',
    target=0.6,
    # checker='value > target'
)
def eval_safe(output):
    time.sleep(3)
    if random.random() < 0.5:
        return True
    else:
        return False
    

results = evaluate(
    function=lambda user_input: user_input,
    dataset=[
        {"user_input": "hi"},
        {"user_input": "hello"},
        {"user_input": "how are you?"}
    ] * 5,
    evaluators=[eval_safe]
)
