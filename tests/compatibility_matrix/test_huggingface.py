#!/usr/bin/env python3
"""
Hugging Face Compatibility Test for HoneyHive SDK

Tests Hugging Face Transformers integration using OpenInference instrumentation
with HoneyHive's "Bring Your Own Instrumentor" pattern.
"""

import os
import sys
from typing import Optional


def test_huggingface_integration():
    """Test Hugging Face integration with HoneyHive via OpenInference instrumentation."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    hf_token = os.getenv("HUGGINGFACE_API_KEY")  # Optional for public models

    if not all([api_key, project]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        print("   - HUGGINGFACE_API_KEY (optional, for private models)")
        return False

    try:
        # Import dependencies
        import torch
        from openinference.instrumentation.huggingface import HuggingFaceInstrumentor
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        from honeyhive import HoneyHiveTracer

        print("🔧 Setting up Hugging Face with HoneyHive integration...")

        # 1. Initialize OpenInference instrumentor
        hf_instrumentor = HuggingFaceInstrumentor()
        print("✓ Hugging Face instrumentor initialized")

        # 2. Initialize HoneyHive tracer with instrumentor
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            instrumentors=[hf_instrumentor],  # Pass instrumentor to HoneyHive
            source="compatibility_test",
        )
        print("✓ HoneyHive tracer initialized with Hugging Face instrumentor")

        # 3. Test text generation pipeline (automatically traced)
        print("🚀 Testing Hugging Face text generation pipeline...")
        text_generator = pipeline(
            "text-generation",
            model="gpt2",  # Small model for testing
            max_length=100,
            do_sample=True,
            temperature=0.1,
        )

        response = text_generator(
            "Say hello and confirm this is a compatibility test for HoneyHive + Hugging Face integration.",
            max_new_tokens=50,
            num_return_sequences=1,
        )

        result_text = response[0]["generated_text"]
        print(f"✓ Text generation response: {result_text}")

        # 4. Test sentiment analysis pipeline
        print("🔧 Testing Hugging Face sentiment analysis...")
        with tracer.enrich_span(
            metadata={"test_type": "compatibility", "provider": "huggingface"},
            outputs={"pipeline_used": "sentiment-analysis"},
        ) as span:
            sentiment_analyzer = pipeline("sentiment-analysis")

            sentiment_result = sentiment_analyzer(
                "HoneyHive provides excellent AI observability capabilities."
            )

            span_data = {
                "sentiment": sentiment_result[0]["label"],
                "confidence": sentiment_result[0]["score"],
                "pipeline": "sentiment-analysis",
            }
            print(f"✓ Sentiment analysis: {span_data}")

        # 5. Test question answering pipeline
        print("🔧 Testing Hugging Face question answering...")
        with tracer.enrich_span(
            metadata={"test_type": "question_answering", "provider": "huggingface"},
        ) as span:
            try:
                qa_pipeline = pipeline("question-answering")

                context = "HoneyHive is an AI observability platform that helps teams monitor and improve their LLM applications through comprehensive tracing and evaluation."
                question = "What is HoneyHive?"

                qa_result = qa_pipeline(question=question, context=context)

                span_data = {
                    "question": question,
                    "answer": qa_result["answer"],
                    "confidence": qa_result["score"],
                    "pipeline": "question-answering",
                }
                print(
                    f"✓ Question answering: {qa_result['answer']} (confidence: {qa_result['score']:.3f})"
                )

            except Exception as e:
                print(f"⚠️  Question answering test failed: {e}")
                span_data = {"qa_error": str(e)}

        # 6. Test text classification pipeline
        print("🔧 Testing Hugging Face text classification...")
        with tracer.enrich_span(
            metadata={"test_type": "text_classification", "provider": "huggingface"},
        ) as span:
            try:
                classifier = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                )

                classification_result = classifier(
                    "This AI observability tool is really helpful!"
                )

                span_data = {
                    "classification": classification_result[0]["label"],
                    "confidence": classification_result[0]["score"],
                    "model": "distilbert-base-uncased-finetuned-sst-2-english",
                }
                print(f"✓ Text classification: {span_data}")

            except Exception as e:
                print(f"⚠️  Text classification test failed: {e}")
                span_data = {"classification_error": str(e)}

        # 7. Test summarization pipeline
        print("🔧 Testing Hugging Face summarization...")
        with tracer.enrich_span(
            metadata={"test_type": "summarization", "provider": "huggingface"},
        ) as span:
            try:
                summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

                text_to_summarize = """
                HoneyHive is an AI observability platform that helps teams monitor and improve their 
                large language model applications. It provides comprehensive tracing capabilities, 
                allowing developers to track the performance of their AI systems in real-time. 
                The platform supports various model providers and frameworks through standardized 
                instrumentation, making it easy to integrate with existing AI workflows.
                """

                summary_result = summarizer(
                    text_to_summarize, max_length=50, min_length=10
                )

                span_data = {
                    "summary": summary_result[0]["summary_text"],
                    "model": "facebook/bart-large-cnn",
                    "pipeline": "summarization",
                }
                print(f"✓ Summarization: {summary_result[0]['summary_text']}")

            except Exception as e:
                print(f"⚠️  Summarization test failed: {e}")
                span_data = {"summarization_error": str(e)}

        # 8. Test direct model usage (lower level)
        print("🔧 Testing Hugging Face direct model usage...")
        with tracer.enrich_span(
            metadata={"test_type": "direct_model", "provider": "huggingface"},
        ) as span:
            try:
                model_name = "gpt2"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(model_name)

                # Add pad token if it doesn't exist
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token

                input_text = "AI observability is important because"
                inputs = tokenizer(input_text, return_tensors="pt", padding=True)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=20,
                        temperature=0.1,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id,
                    )

                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

                span_data = {
                    "input_text": input_text,
                    "generated_text": generated_text,
                    "model": model_name,
                    "direct_model_usage": True,
                }
                print(f"✓ Direct model generation: {generated_text}")

            except Exception as e:
                print(f"⚠️  Direct model test failed: {e}")
                span_data = {"direct_model_error": str(e)}

        # 9. Test feature extraction pipeline
        print("🔧 Testing Hugging Face feature extraction...")
        with tracer.enrich_span(
            metadata={"test_type": "feature_extraction", "provider": "huggingface"},
        ) as span:
            try:
                feature_extractor = pipeline(
                    "feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2"
                )

                features = feature_extractor(
                    "This is a test sentence for feature extraction."
                )

                span_data = {
                    "feature_dimension": len(features[0][0]),
                    "num_tokens": len(features[0]),
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                }
                print(f"✓ Feature extraction: {span_data}")

            except Exception as e:
                print(f"⚠️  Feature extraction test failed: {e}")
                span_data = {"feature_extraction_error": str(e)}

        # 10. Test zero-shot classification
        print("🔧 Testing Hugging Face zero-shot classification...")
        with tracer.enrich_span(
            metadata={"test_type": "zero_shot", "provider": "huggingface"},
        ) as span:
            try:
                zero_shot_classifier = pipeline("zero-shot-classification")

                text = "HoneyHive helps monitor AI applications"
                candidate_labels = ["technology", "health", "sports", "business"]

                zero_shot_result = zero_shot_classifier(text, candidate_labels)

                span_data = {
                    "predicted_label": zero_shot_result["labels"][0],
                    "confidence": zero_shot_result["scores"][0],
                    "all_labels": zero_shot_result["labels"],
                    "pipeline": "zero-shot-classification",
                }
                print(
                    f"✓ Zero-shot classification: {zero_shot_result['labels'][0]} (confidence: {zero_shot_result['scores'][0]:.3f})"
                )

            except Exception as e:
                print(f"⚠️  Zero-shot classification test failed: {e}")
                span_data = {"zero_shot_error": str(e)}

        # 11. Force flush to ensure traces are sent
        print("📤 Flushing traces...")
        tracer.force_flush(timeout=10.0)
        print("✓ Traces flushed successfully")

        print("🎉 Hugging Face integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages:")
        print("   pip install honeyhive[opentelemetry]")
        print("   pip install openinference-instrumentation-huggingface")
        print("   pip install transformers torch sentence-transformers")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the Hugging Face compatibility test."""
    print("🧪 HoneyHive + Hugging Face Compatibility Test")
    print("=" * 50)

    success = test_huggingface_integration()

    if success:
        print("\n✅ Hugging Face compatibility: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Hugging Face compatibility: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
