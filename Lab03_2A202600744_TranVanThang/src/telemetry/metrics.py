import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage) # Mock cost calculation
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Implement real pricing logic for OpenAI and Gemini models.
        """
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        m_lower = model.lower()
        if "gpt-4" in m_lower or "gpt-3.5" in m_lower or "openai" in m_lower:
            # GPT-4o pricing (Standard)
            input_cost = (prompt_tokens / 1_000_000) * 5.00
            output_cost = (completion_tokens / 1_000_000) * 15.00
            return input_cost + output_cost
        elif "gemini" in m_lower or "google" in m_lower:
            # Gemini 2.0 Flash pricing (Standard)
            input_cost = (prompt_tokens / 1_000_000) * 0.075
            output_cost = (completion_tokens / 1_000_000) * 0.30
            return input_cost + output_cost
        else:
            # Fallback local/dummy pricing
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            return (total_tokens / 1000) * 0.0015

# Global tracker instance
tracker = PerformanceTracker()
