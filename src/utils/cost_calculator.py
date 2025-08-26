"""
Cost calculation utilities
"""
from typing import Dict, Any
from ..models import CostReport


class CostCalculator:
    """Calculate API usage costs"""
    
    # Gemini Flash 2.5 Lite pricing (USD per 1M tokens)
    INPUT_COST_PER_MILLION = 0.075
    OUTPUT_COST_PER_MILLION = 0.30
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def add_token_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Add token usage to running total"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        
        self.total_cost += input_cost + output_cost
    
    def get_cost_report(self) -> CostReport:
        """Get comprehensive cost report"""
        input_cost = (self.total_input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (self.total_output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        
        return CostReport(
            input_tokens=self.total_input_tokens,
            output_tokens=self.total_output_tokens,
            total_tokens=self.total_input_tokens + self.total_output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=input_cost + output_cost
        )
    
    def print_cost_summary(self) -> None:
        """Print formatted cost summary"""
        cost_report = self.get_cost_report()
        
        print("\nMALIYET ANALİZİ:")
        print(f"Toplam Token: {cost_report.total_tokens:,}")
        print(f"Input Token: {cost_report.input_tokens:,}")
        print(f"Output Token: {cost_report.output_tokens:,}")
        print(f"Toplam Maliyet: ${cost_report.total_cost_usd:.6f}")
        print(f"Input Maliyeti: ${cost_report.input_cost_usd:.6f}")
        print(f"Output Maliyeti: ${cost_report.output_cost_usd:.6f}")
    
    @staticmethod
    def calculate_single_operation_cost(input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a single operation"""
        input_cost = (input_tokens / 1_000_000) * CostCalculator.INPUT_COST_PER_MILLION
        output_cost = (output_tokens / 1_000_000) * CostCalculator.OUTPUT_COST_PER_MILLION
        return input_cost + output_cost
