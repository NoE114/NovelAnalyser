import os
import json
from typing import List, Dict, Any
from groq import Groq
from src.reasoning_validation.schemas import ReasoningTrace, ClassificationResult

# Initialize Groq client
# In a real app, strict dependency injection is better, but here we instantiate for simplicity
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def reason_with_llm(backstory: str, evidence: List[Dict], config: Dict[str, Any]) -> ClassificationResult:
    """
    Orchestrates the reasoning process: Prompt -> LLM -> Parse -> Initial Result.
    """
    
    # 1. Format Evidence
    evidence_text = ""
    for i, chunk in enumerate(evidence):
        evidence_text += f"[Node {chunk['chunk_id']}] (Chapter: {chunk['chapter']}):\n{chunk['text']}\n\n"
        
    # 2. Construct Prompt (Strictly constrained)
    system_prompt = """You are an EVIDENCE-GROUNDED REASONING ENGINE.
    Your task is to classify the provided narrative context based on the query.
    
    RULES:
    1. You must ONLY use the provided evidence. Do not use external knowledge.
    2. Every fact you state must be supported by a verbatim quote from the evidence.
    3. You must evaluate valid alternative explanations.
    4. Output MUST be valid JSON matching the ReasoningTrace schema.
    5. If evidence is insufficient, set status to REJECTION.
    """
    
    user_prompt = f"""
    QUERY: {backstory}
    
    EVIDENCE:
    {evidence_text}
    
    Output the JSON ReasoningTrace.
    """
    
    # 3. Call LLM
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Or specific model from config
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=config.get('temperature', 0.2),
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        
        # 4. Parse and Validate Schema (Basic parsing here, Validation module does the heavy lifting)
        trace_data = json.loads(response_content)
        trace = ReasoningTrace(**trace_data)
        
        # Create Result Wrapper
        result = ClassificationResult(
            status="SUCCESS",
            target_class=trace.primary_hypothesis.hypothesis_text, # Simplified mapping
            confidence=trace.primary_hypothesis.confidence_score,
            reasoning_trace=trace
        )
        return result
        
    except Exception as e:
        # Fallback for LLM errors or parsing errors
        print(f"LLM Error: {e}")
        # Return a rejection result
        # We need to construct a valid placeholder or re-raise
        # For safety, we return a REJECTION result
        return ClassificationResult(
            status="REJECTION", 
            confidence=0.0, 
            reasoning_trace=ReasoningTrace( # Dummy trace to valid schema
                primary_hypothesis={"hypothesis_text": "Error", "supporting_evidence": [], "confidence_score": 0.0},
                alternatives_considered=[],
                logical_steps=["System Error encountered"]
            ),
            rejection_reason=str(e)
        )
