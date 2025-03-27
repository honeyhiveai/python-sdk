import boto3
import json
import os
from honeyhive import evaluate, enrich_span, trace

class ClaimSummarizer:
    
    def __init__(self, model_id="meta.llama3-70b-instruct-v1:0"):
        # Initialize Bedrock client with credentials from environment
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-west-2")
        )
        self.model_id = model_id
    
    @trace()
    def generate_summary(self, log_content, max_sentences=8, ground_truth=None):
        # Validate inputs
        if log_content is None:
            return "No log content provided to summarize."
            
        # Ensure log_content is a string
        log_content = str(log_content)
        
        # Define prompt template
        prompt_template = """
        Please provide a highly concise summary of the following insurance claim log notes in {{max_sentences}} sentences or fewer.
        Focus on:
        1. The nature of the claim
        2. Current status
        3. Important actions taken
        4. Next steps required
        
        LOG NOTES:
        {{log_notes}}
        
        SUMMARY:
        """
        
        # Create actual prompt by formatting the template
        prompt = prompt_template.replace("{{max_sentences}}", str(max_sentences)).replace("{{log_notes}}", log_content)
        
        # Create the request body for Bedrock
        request_body = {
            "prompt": prompt,
            "max_gen_len": 512,
            "temperature": 0.1,
            "top_p": 0.9,
        }
        
        # Extract hyperparams from request_body
        hyperparams = {k: v for k, v in request_body.items() if k != "prompt"}
        
        # Create template in OpenAI format with placeholders
        template = [
            {
                "role": "user",
                "content": prompt_template
            }
        ]
        
        # Invoke the model
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response.get("body").read())
        summary = response_body.get("generation", "")
        
        # Clean up the summary if needed
        summary = summary.strip()
        
        # Prepare feedback if ground truth is available
        feedback = {}
        if ground_truth and "result" in ground_truth:
            feedback["ground_truth"] = ground_truth["result"]
        
        # Single enrich_span call with all information
        enrich_span(
            config={
                "model": self.model_id,
                "template": template,
                "hyperparameters": hyperparams
            },
            metrics={
                "summary_length": len(summary.split('.')),
                "word_count": len(summary.split())
            },
            feedback=feedback
        )
        
        return summary

def summarize_claim(inputs, ground_truths=None):
    # Set AWS credentials
    # os.environ["AWS_ACCESS_KEY_ID"] = ""
    # os.environ["AWS_SECRET_ACCESS_KEY"] = ""
    # os.environ["AWS_REGION"] = "us-west-2"
    
    # Extract inputs from the _params_ dictionary
    params = inputs.get("_params_", {})
    log_content = params.get("log_content")
    max_sentences = params.get("max_sentences", 6)
    
    # Initialize the summarizer
    summarizer = ClaimSummarizer()
    
    # Generate summary, passing ground_truth to the function
    summary = summarizer.generate_summary(
        log_content=log_content, 
        max_sentences=max_sentences,
        ground_truth=ground_truths
    )
    
    return summary

def test_eval(outputs):
    return 5

if __name__ == "__main__":
    # Run the experiment
    evaluate(
        function=summarize_claim,
        hh_api_key="MGc0cnl6MWh3MDk5OXhndGgycm92Y3A=",
        hh_project="e2e",
        name="Claims Summarizer Experiment",
        dataset_id="67c60a93d3333713242d30e0",
        evaluators=[test_eval],
        run_concurrently=True,
        verbose=True,
        server_url='https://nationwide.api.honeyhive.ai'
        # server_url='http://localhost:3000'
    )