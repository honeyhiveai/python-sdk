from honeyhive import HoneyHiveTracer, trace, enrich_span, enrich_session

import time
import os

import openai

HH_API_KEY = os.environ.get("HH_API_KEY")
HH_PROJECT = os.environ.get("HH_PROJECT")

# place the code below at the beginning of your application execution
HoneyHiveTracer.init(
    api_key=HH_API_KEY,
    project=HH_PROJECT,
)

enrich_session(
    metadata={"hello": "bonjour"}, 
    feedback={"mood": "sleepy"}, 
    metrics={"score": 1}
)

@trace(event_type="chain")
def get_meaning_of_life():
    enrich_span(
        metadata={"dataset2": "lifeee"}, 
        feedback={"score": "good"}, 
        inputs={"a": 1}, 
        outputs={"b": 2}, 
        error="this is malarky"
    )
    time.sleep(0.1)
    return "42"

@trace(metadata={"source": "outer metadata"})
def get_prompt(a=1):
    enrich_span(config={"model": "inner model"}, metadata={"dataset": "enrich get_prompt before"})
    meaning = get_meaning_of_life()
    enrich_span(metadata={"dataset2": "enrich get_prompt after"})
    return "What is the capital of the moon?"

@trace(config={"model": "gpt-4o-mini"})
def main():
    enrich_span(config={"something": "agi"})
    prompt = get_prompt()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1
    )

    print(response.choices[0].message.content)

@trace()
def test_enrich_span():
    enrich_span(metadata={"dataset1": "hello"})
    time.sleep(0.05)
    meaning = get_meaning_of_life()
    enrich_span(
        metadata={"dataset3": "world"}, 
        feedback={"score": "baad"}, 
        inputs={"a": 5}, 
        outputs={"b": 267}, 
        error="this is anti-agi"
    )
    main()
    enrich_span(metadata={"dataset3": "universe"}) # should update metadata instead of replace
    enrich_span(error="this is pro-agi")
    return 'ok'

test_enrich_span()

HoneyHiveTracer.flush()
