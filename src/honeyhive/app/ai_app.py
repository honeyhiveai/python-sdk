import random
from openai import OpenAI

client = OpenAI()

from honeyhive import config, trace

@trace(eval='eval_profanity')
def get_ai_response(user_input: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": config.system_prompt}, 
            {"role": "user", "content": user_input}
        ]
    )
    content = response.choices[0].message.content

    # sometimes return a malicious output
    if random.random() < 0.5:
        content = "Fockin'ell!"
    
    return content

def main():
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit condition
        if user_input.lower() in ['bye', '', 'q']:
            print("\nAI: Goodbye! Have a great day!")
            break
        
        # Get and display AI response
        if user_input:
            print("\nAI: ", end='')
            print(get_ai_response(user_input))
        print()


if __name__ == "__main__":
    main()
