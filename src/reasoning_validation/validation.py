from typing import List, Dict, Any
from .schemas import ClassificationResult, EvidenceSpan
import yaml # Assuming PyYAML is installed

class Validator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_confidence = config['validation'].get('reject_if_confidence_below', 0.4)
        self.min_evidence_count = config['validation'].get('min_evidence', 3)
        self.require_quote_integrity = config['validation']['quote_integrity'].get('must_match_source_substring', True)

    def validate_classification(self, result: ClassificationResult, retrieved_context: List[Dict[str, str]]) -> ClassificationResult:
        """
        Validates the classification result against system rules.
        Modifies the result status to REJECTION if checks fail.
        """
        # 1. Check Confidence
        if result.confidence < self.min_confidence:
            result.status = "REJECTION"
            result.rejection_reason = f"Confidence {result.confidence} below threshold {self.min_confidence}"
            return result

        # 2. Check Evidence Count
        primary_evidence = result.reasoning_trace.primary_hypothesis.supporting_evidence
        if len(primary_evidence) < self.min_evidence_count:
            result.status = "REJECTION"
            result.rejection_reason = f"Insufficient evidence: {len(primary_evidence)} spans provided, required {self.min_evidence_count}"
            return result

        # 3. Check Quote Integrity
        if self.require_quote_integrity:
            for span in primary_evidence:
                if not self._verify_quote_in_context(span, retrieved_context):
                    result.status = "REJECTION"
                    result.rejection_reason = f"Quote fabrication detected: '{span.quote_text[:30]}...'"
                    return result
        
        return result

    def _verify_quote_in_context(self, span: EvidenceSpan, context_nodes: List[Dict[str, str]]) -> bool:
        """
        Verifies that the span.quote_text exists verbatim in the corresponding chapter/node.
        """
        # In a real implementation, we strictly check node_id matching.
        # Here we check if the text exists in the specific referenced node.
        target_node = next((n for n in context_nodes if n.get('id') == span.source_node_id), None)
        
        if not target_node:
            # If node not found in retrieved context, it's a hallucination or reference error
            return False
            
        source_text = target_node.get('text', "")
        # Strict substring match
        return span.quote_text in source_text
