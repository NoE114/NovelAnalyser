from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class EvidenceSpan(BaseModel):
    """
    Represents a specific quote retrieval from the text.
    """
    quote_text: str = Field(..., description="Verbatim text from the source node.")
    chapter_id: str = Field(..., description="ID of the chapter containing the quote.")
    paragraph_index: Optional[int] = Field(None, description="Index of the paragraph within the chapter.")
    source_node_id: str = Field(..., description="Pathway node ID for verification.")

class AlternativeHypothesis(BaseModel):
    """
    Represents a potential causal explanation that is evaluated.
    """
    hypothesis_text: str = Field(..., description="The explanation.")
    supporting_evidence: List[EvidenceSpan] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    is_contradicted: bool = Field(False, description="True if evidence explicitly contradicts this.")

class ReasoningTrace(BaseModel):
    """
    The core reasoning object produced by the LLM.
    """
    primary_hypothesis: AlternativeHypothesis
    alternatives_considered: List[AlternativeHypothesis]
    logical_steps: List[str] = Field(..., description="Step-by-step derivation of the conclusion.")
    
    @field_validator('logical_steps')
    def validate_steps(cls, v):
        if len(v) < 2:
            raise ValueError("Reasoning must have at least 2 logical steps.")
        return v

class ClassificationResult(BaseModel):
    """
    Final output schema for the classification task.
    """
    status: Literal["SUCCESS", "REJECTION", "CONTRADICTION"]
    target_class: Optional[str] = Field(None, description="The resulting class (e.g., 'Revenge', 'Accident').")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning_trace: ReasoningTrace
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if status is not SUCCESS.")

    class Config:
        extra = "forbid"
