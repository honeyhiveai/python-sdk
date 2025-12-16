"""
Add Tracing to Existing Apps - All Examples

This matches all the code examples in tutorials/add-tracing-5min.mdx
Shows how to add HoneyHive tracing to existing applications with just 5 lines.

Run: uv run python examples/tutorials/add_tracing_5min.py
"""
# ========== ADD THESE 5 LINES TO YOUR EXISTING APP ==========
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.anthropic import AnthropicInstrumentor

tracer = HoneyHiveTracer.init(source="docs")  # Reads HH_API_KEY and HH_PROJECT from env
OpenAIInstrumentor().instrument(tracer_provider=tracer.provider)
AnthropicInstrumentor().instrument(tracer_provider=tracer.provider)
# ========== END OF CHANGES ==========

import openai
import anthropic
from dotenv import load_dotenv

load_dotenv()

print("Add Tracing to Existing Apps - Examples\n")
print("=" * 50)


# ========== EXAMPLE 1: SIMPLE CHATBOT (OpenAI) ==========
def simple_chatbot_example():
    """Example 1 from docs: Simple chatbot with OpenAI"""
    print("\n📝 Example 1: Simple Chatbot")
    print("-" * 50)
    
    client = openai.OpenAI()
    
    def chat(message):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    
    result = chat("Hello, how are you?")
    print(f"Response: {result}")
    print("✅ Chatbot call traced!\n")


# ========== EXAMPLE 2: MULTI-STEP APPLICATION (Anthropic) ==========
def multi_step_example():
    """Example 2 from docs: Multi-step application with Anthropic"""
    print("\n📝 Example 2: Multi-Step Application")
    print("-" * 50)
    
    def summarize_text(text):
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": f"Summarize: {text}"}]
        )
        return response.content[0].text

    def generate_questions(summary):
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": f"Generate 3 questions: {summary}"}]
        )
        return response.content[0].text
    
    article = """
    Artificial intelligence has transformed software development in recent years.
    Machine learning models can now assist developers with code completion, bug detection,
    and even generating entire functions. This has led to significant productivity gains
    across the industry.
    """
    
    print("Step 1: Summarizing article...")
    summary = summarize_text(article)
    print(f"Summary: {summary[:100]}...\n")
    
    print("Step 2: Generating questions...")
    questions = generate_questions(summary)
    print(f"Questions: {questions[:100]}...")
    print("✅ Both calls traced - see the full chain in HoneyHive!\n")


# ========== EXAMPLE 3: MULTIPLE PROVIDERS ==========
def multiple_providers_example():
    """Multiple providers example from docs"""
    print("\n📝 Example 3: Multiple Providers")
    print("-" * 50)
    
    def ask_openai(question):
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content

    def ask_anthropic(question):
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": question}]
        )
        return response.content[0].text
    
    question = "What is the capital of France?"
    
    print("Asking OpenAI...")
    openai_answer = ask_openai(question)
    print(f"OpenAI: {openai_answer}\n")
    
    print("Asking Anthropic...")
    anthropic_answer = ask_anthropic(question)
    print(f"Anthropic: {anthropic_answer}")
    print("✅ Both providers traced!\n")


def main():
    """Run all examples"""
    # Run Example 1: Simple Chatbot
    simple_chatbot_example()
    
    # Run Example 2: Multi-Step Application
    multi_step_example()
    
    # Run Example 3: Multiple Providers
    multiple_providers_example()
    
    print("=" * 50)
    print("\n✅ All examples complete!")
    print("👉 Check https://app.honeyhive.ai for your traces\n")


if __name__ == "__main__":
    main()
