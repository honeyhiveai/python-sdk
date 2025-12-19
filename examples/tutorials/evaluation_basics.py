"""
Tutorial: Run Your First Experiment
From: tutorials/evaluation-basics.mdx

Compares two prompts for customer support intent classification.
Shows how prompt engineering affects accuracy on a realistic task.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from honeyhive import HoneyHive
from honeyhive.experiments import evaluate, compare_runs

load_dotenv()

client = OpenAI()

# Two different prompts to compare
BAD_PROMPT = """You are a customer support assistant. Classify the customer's intent."""

GOOD_PROMPT = """Classify this customer support message into exactly ONE category.

Categories:
- billing: payment issues, invoices, charges, refunds, pricing
- technical: bugs, errors, not working, how to use features
- account: login, password, profile, settings, permissions
- shipping: delivery, tracking, address, returns, lost packages
- general: other questions, feedback, compliments, complaints

Reply with ONLY the category name, nothing else.

Message: {text}
Category:"""


def classify_with_bad_prompt(datapoint):
    """Classify intent using a vague prompt."""
    inputs = datapoint.get("inputs", {})
    text = inputs.get("text", "")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": BAD_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.3  # Slight variation
    )
    
    return {"intent": response.choices[0].message.content.strip().lower()}


def classify_with_good_prompt(datapoint):
    """Classify intent using a well-structured prompt."""
    inputs = datapoint.get("inputs", {})
    text = inputs.get("text", "")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": GOOD_PROMPT.format(text=text)}
        ],
        temperature=0
    )
    
    return {"intent": response.choices[0].message.content.strip().lower()}


# Dataset: Customer support messages with labeled intents
# Mix of clear and ambiguous cases
dataset = [
    # Clear billing
    {
        "inputs": {"text": "I was charged twice for my subscription this month. Please refund the duplicate charge."},
        "ground_truth": {"intent": "billing"}
    },
    # Clear technical
    {
        "inputs": {"text": "The export button isn't working. I click it but nothing happens. Getting error code 500."},
        "ground_truth": {"intent": "technical"}
    },
    # Clear account
    {
        "inputs": {"text": "I forgot my password and the reset email never arrived. Can you help me get back in?"},
        "ground_truth": {"intent": "account"}
    },
    # Clear shipping
    {
        "inputs": {"text": "My order was supposed to arrive 5 days ago. Tracking says delivered but I never got it."},
        "ground_truth": {"intent": "shipping"}
    },
    # Ambiguous: billing or account? (billing - about charges)
    {
        "inputs": {"text": "Why am I being charged for premium features? I only signed up for the free plan."},
        "ground_truth": {"intent": "billing"}
    },
    # Ambiguous: technical or account? (account - about permissions)
    {
        "inputs": {"text": "I can't access the admin dashboard. It says I don't have permission but I'm the owner."},
        "ground_truth": {"intent": "account"}
    },
    # Ambiguous: shipping or general? (shipping - about returns)
    {
        "inputs": {"text": "I want to return this item. It's not what I expected from the photos."},
        "ground_truth": {"intent": "shipping"}
    },
    # Tricky: sounds technical but it's billing
    {
        "inputs": {"text": "The payment page keeps failing. I've tried 3 different cards and none work."},
        "ground_truth": {"intent": "billing"}
    },
    # General - feedback
    {
        "inputs": {"text": "Just wanted to say your support team was amazing last time. Thanks for the great service!"},
        "ground_truth": {"intent": "general"}
    },
    # Tricky: multiple intents, primary is technical
    {
        "inputs": {"text": "App crashes every time I try to update my profile picture. Started happening after the last update."},
        "ground_truth": {"intent": "technical"}
    },
]


def intent_match(outputs, inputs, ground_truth):
    """Check if intent classification matches expected."""
    actual = outputs.get("intent", "").lower().strip()
    expected = ground_truth.get("intent", "").lower().strip()
    
    # Check if the expected intent appears in the output
    # This handles cases like "billing issue" matching "billing"
    return 1.0 if expected in actual or actual == expected else 0.0


if __name__ == "__main__":
    print("=" * 70)
    print("Tutorial: Comparing Prompts for Intent Classification")
    print("=" * 70)
    
    # Run with bad prompt
    print("\n📊 Running experiment with VAGUE prompt...")
    print(f"   System: '{BAD_PROMPT}'")
    result_bad = evaluate(
        function=classify_with_bad_prompt,
        dataset=dataset,
        evaluators=[intent_match],
        name="intent-vague-prompt"
    )
    
    print(f"\n✅ Vague prompt experiment complete!")
    print(f"📊 Run ID: {result_bad.run_id}")
    
    # Run with good prompt
    print("\n" + "=" * 70)
    print("📊 Running experiment with STRUCTURED prompt...")
    print(f"   Includes category definitions and format instructions")
    result_good = evaluate(
        function=classify_with_good_prompt,
        dataset=dataset,
        evaluators=[intent_match],
        name="intent-structured-prompt"
    )
    
    print(f"\n✅ Structured prompt experiment complete!")
    print(f"📊 Run ID: {result_good.run_id}")
    
    # Compare runs programmatically
    print("\n" + "=" * 70)
    print("📊 Comparing runs programmatically...")
    
    client = HoneyHive()
    comparison = compare_runs(
        client=client,
        new_run_id=result_good.run_id,
        old_run_id=result_bad.run_id
    )
    
    print(f"\n📈 Comparison Results:")
    print(f"   Common datapoints: {comparison.common_datapoints}")
    
    # Show metric deltas
    for metric_name, delta in comparison.metric_deltas.items():
        old_val = delta.get("old_aggregate", 0) or 0
        new_val = delta.get("new_aggregate", 0) or 0
        change = new_val - old_val
        status = "✅ improved" if change > 0 else ("⚠️ degraded" if change < 0 else "— same")
        print(f"   {metric_name}: {old_val:.2f} → {new_val:.2f} ({change:+.2f}) {status}")
    
    print("\n" + "=" * 70)
    print("✅ Tutorial complete!")
    print("\nView results in dashboard: https://app.honeyhive.ai/evaluate")
    print("=" * 70)
