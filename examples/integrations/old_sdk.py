import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from honeyhive import HoneyHiveTracer, trace, enrich_span
load_dotenv()
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Place the code below at the beginning of your application to initialize the tracer
HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="sdk", # Your HoneyHive project name
    source='dev', #Optional
    session_name='Test Session', #Optional
    server_url="https://api.staging.honeyhive.ai"
)
# Additionally, trace any function in your code using @trace / @atrace decorator
@trace
def call_openai(user_input):
    client = OpenAI()
     # Example: Add feedback data for HoneyHive evaluation
    # if user_input.strip().lower() == "what is the capital of france?":
    #     HoneyHiveTracer.add_feedback({
    #         "ground_truth": "The capital of France is Paris.",
    #         "keywords": ["Paris", "France", "capital"]
    #     })
    completion = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{"role":"user","content": user_input}]
    )
    return completion.choices[0].message.content
# @app.route("/")
# def index():
#     return render_template("index.html")
# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     user_input = data.get("message", "")
#     try:
#         reply = call_openai(user_input)
#         return jsonify({"reply": reply})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
# if __name__ == "__main__":
#     app.run(debug=True)
call_openai("hi")