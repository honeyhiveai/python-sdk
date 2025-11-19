from honeyhive import HoneyHive
from honeyhive.experiments import evaluate
import os
from dotenv import load_dotenv
from datetime import datetime
from honeyhive.api import DatasetsAPI, DatapointsAPI, MetricsAPI
from pydantic import BaseModel
from uuid import uuid4
from honeyhive.models.generated import ReturnType
from honeyhive.models import (
    CreateDatapointRequest,
    CreateDatasetRequest,
    Metric,
)
from honeyhive import enrich_span

load_dotenv()

DATASET_NAME = "sample-honeyhive-9-30-25"


def invoke_summary_agent(**kwargs):
    return "The American Shorthair is a pedigreed cat breed, originally known as the Domestic Shorthair, that was among the first CFA-registered breeds in 1906 and was renamed in 1966 to distinguish it from random-bred domestic short-haired cats while highlighting its American origins."

dataset = [
    {
        "inputs": {
            "context": "The Poodle, called the Pudel in German and the Caniche in French, is a breed of water dog. The breed is divided into four varieties based on size, the Standard Poodle, Medium Poodle, Miniature Poodle and Toy Poodle, although the Medium Poodle is not universally recognised. They have a distinctive thick, curly coat that comes in many colours and patterns, with only solid colours recognised by major breed registries. Poodles are active and intelligent, and are particularly able to learn from humans. Poodles tend to live 10–18 years, with smaller varieties tending to live longer than larger ones."
        },
        "ground_truth": {
            "result": "The Poodle is an intelligent water dog breed that comes in four size varieties with a distinctive curly coat, known for its trainability and relatively long lifespan of 10-18 years."
        },
    },
    {
        "inputs": {
            "context": 'The American Shorthair is a pedigree cat breed, with a strict conformation standard, as set by cat fanciers of the breed and North American cat fancier associations such as The International Cat Association (TICA) and the CFA. The breed is accepted by all North American cat registries. Originally known as the Domestic Shorthair, in 1966 the breed was renamed the American Shorthair to better represent its "all-American" origins and to differentiate it from other short-haired breeds. The name American Shorthair also reinforces the breed\'s pedigreed status as distinct from the random-bred non-pedigreed domestic short-haired cats in North America, which may nevertheless resemble the American Shorthair. Both the American Shorthair breed and the random-bred cats from which the breed is derived are sometimes called working cats because they were used for controlling rodent populations, on ships and farms. The American Shorthair (then referred to as the Domestic Shorthair) was among the first five breeds that were registered by the CFA in 1906.'
        },
        "ground_truth": {
            "result": "The American Shorthair is a pedigreed cat breed, originally known as the Domestic Shorthair, that was among the first CFA-registered breeds in 1906 and was renamed in 1966 to distinguish it from random-bred domestic short-haired cats while highlighting its American origins."
        },
    },
]


if __name__ == "__main__":
    def evaluation_function(datapoint):
        inputs = datapoint.get("inputs", {})
        context = inputs.get("context", "")
        enrich_span(metrics={"input_length": len(context)})
        return {
            "answer": invoke_summary_agent(**{"context": context})
        }

    result = evaluate(
        function=evaluation_function,
        dataset=dataset,
        api_key=os.environ["HH_API_KEY"],
        project=os.environ["HH_PROJECT"],
        name=f"{DATASET_NAME}-{datetime.now().isoformat()}",
        verbose=True,  # Enable verbose to see output enrichment
    )

    print(result)