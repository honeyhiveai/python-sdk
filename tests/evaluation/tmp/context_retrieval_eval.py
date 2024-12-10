from honeyhive.evaluation import evaluate

# find more evaluators here: https://...
from realign import profanity_evaluator

# replace with my application
def my_pipeline(prompt, joke):
    return joke

# replace with my evaluator
# @evaluator
# def profanity_evaluator(output):
#     return 1 if output in ["fuck", "shit", "asshole"] else 0

def fail_on_profanity():
    # replace with my dataset
    profs = ["fuck", "shit", "asshole"]

    results = evaluate(
        name='Profanity Experiment',
        function=my_pipeline,
        dataset=profs,
        evaluators=['profanity_evaluator']
    )

    print(results.permalink)
    print(results.summary)

    assert results.all()
