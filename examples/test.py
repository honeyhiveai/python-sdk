from openai import OpenAI
from openinference.instrumentation.openai import OpenAIInstrumentor

from honeyhive import HoneyHiveTracer, trace

# Initialize tracer
tracer = HoneyHiveTracer.init(
    verbose=True,
)

# Initialize instrumentor - auto-traces OpenAI calls
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)


# Trace any function in your code using @trace() decorator
@trace()
def call_openai():
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What is the meaning of life?"}],
    )
    print(completion.choices[0].message.content)


call_openai()
