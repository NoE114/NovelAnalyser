import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from src.pathway_pipeline.chunking import chunk_novels # Skipped due to missing dependency
from src.reasoning_validation.schemas import ReasoningTrace, ClassificationResult, EvidenceSpan, AlternativeHypothesis
from src.reasoning_validation.validation import Validator

def test_chunking():
    print("Testing Chunking Logic... SKIPPED (Pathway not installed)")
    pass

def test_validation_logic():
    print("\nTesting Validation Logic...")
    
    # Mock Config
    config = {
        'validation': {
            'reject_if_confidence_below': 0.4,
            'min_evidence': 2,
            'quote_integrity': {'must_match_source_substring': True}
        }
    }
    validator = Validator(config)
    
    # Case 1: Success
    print("Case 1: Valid Result")
    trace = ReasoningTrace(
        primary_hypothesis=AlternativeHypothesis(
            hypothesis_text="Reason A",
            confidence_score=0.9,
            supporting_evidence=[
                EvidenceSpan(quote_text="The sky was blue.", chapter_id="ch1", source_node_id="n1"),
                EvidenceSpan(quote_text="Sun shone bright.", chapter_id="ch1", source_node_id="n1")
            ]
        ),
        alternatives_considered=[],
        logical_steps=["Step 1", "Step 2"]
    )
    result = ClassificationResult(status="SUCCESS", confidence=0.9, reasoning_trace=trace)
    
    context = [{"id": "n1", "text": "The sky was blue. Sun shone bright."}]
    
    validated = validator.validate_classification(result, context)
    assert validated.status == "SUCCESS", f"Expected SUCCESS, got {validated.status}"
    print("  ✅ Passed")

    # Case 2: Low Confidence
    print("Case 2: Low Confidence")
    trace.primary_hypothesis.confidence_score = 0.3
    result.confidence = 0.3
    validated = validator.validate_classification(result, context)
    assert validated.status == "REJECTION", f"Expected REJECTION, got {validated.status}"
    print("  ✅ Passed")

    # Case 3: Quote Fabrication
    print("Case 3: Quote Fabrication")
    trace.primary_hypothesis.confidence_score = 0.9
    result.confidence = 0.9
    trace.primary_hypothesis.supporting_evidence[0].quote_text = "The sky was green."
    validated = validator.validate_classification(result, context)
    assert validated.status == "REJECTION", f"Expected REJECTION (integrity), got {validated.status}"
    print("  ✅ Passed")

if __name__ == "__main__":
    try:
        test_chunking()
        test_validation_logic()
        print("\nAll logical checks passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
