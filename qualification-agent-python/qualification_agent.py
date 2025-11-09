"""
Lead Qualification Agent using AWS Strands Agents SDK
This agent evaluates leads for real estate CRM using a model-driven approach
"""

from strands import Agent, tool
from strands.models import BedrockModel
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from utils import AgentTimer, calculate_cost, print_cost_summary, print_aws_config_status

# Data classes for type safety
@dataclass
class LeadInput:
    id: str
    tenant_id: str
    email: str
    phone: Optional[str] = None
    budget: Optional[str] = None
    years_in_city: Optional[int] = None
    occupation: Optional[str] = None
    source: str = "direct"
    created_at: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class QualificationScore:
    budget_score: int
    intent_score: int
    readiness_score: int
    engagement_score: int
    total_score: int
    confidence: str  # 'high', 'medium', 'low'
    reasoning: str
    strengths: List[str]
    concerns: List[str]
    recommendations: List[str]


# Tool 1: Lead Enrichment
@tool
def enrich_lead(email: str, phone: Optional[str] = None) -> Dict[str, Any]:
    """Enriches lead data by searching for professional and financial indicators.
    
    In production, this would call Clearbit, PeopleDataLabs, or similar APIs.
    
    Args:
        email: The lead's email address
        phone: The lead's phone number (optional)
        
    Returns:
        Dict containing enrichment data including company info and estimated income
    """
    # Tool output is controlled by agent streaming, no need for prints
    
    # Mock enrichment for local testing
    domain = email.split('@')[1]
    is_corporate = domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    
    enrichment = {
        "email": email,
        "is_corporate_email": is_corporate,
        "estimated_income": "$75,000-$125,000" if is_corporate else "$50,000-$100,000",
        "credit_indicators": {
            "has_stable_employment": is_corporate,
            "likely_homeowner": False
        }
    }
    
    if is_corporate:
        enrichment.update({
            "company_info": {
                "name": domain.split('.')[0].title(),
                "industry": "Technology",
                "size": "100-500"
            },
            "linkedin_profile": f"https://linkedin.com/in/{email.split('@')[0]}"
        })
    
    return enrichment


# Tool 2: Calculate Qualification Score
@tool
def calculate_qualification_score(
    lead_data: Dict[str, Any],
    enrichment_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculates a detailed qualification score based on multiple factors.
    Returns scores for budget, intent, readiness, and engagement.
    """
    # Tool output is controlled by agent streaming, no need for prints
    
    # Budget Score (0-30)
    budget_score = 0
    if lead_data.get('budget'):
        budget_score += 10
        try:
            # Handle both string budgets like "$250,000" and numeric budgets
            if isinstance(lead_data['budget'], str):
                budget_num = int(''.join(filter(str.isdigit, lead_data['budget'])))
            else:
                budget_num = int(lead_data['budget'])
                
            if budget_num >= 500000:
                budget_score += 20
            elif budget_num >= 300000:
                budget_score += 15
            elif budget_num >= 200000:
                budget_score += 10
            elif budget_num >= 100000:
                budget_score += 5
        except (ValueError, TypeError):
            # If budget parsing fails, use default score
            budget_score += 5
    budget_score = min(budget_score, 30)
    
    # Intent Score (0-25)
    intent_score = 0
    high_intent_sources = ['direct', 'referral', 'property-listing']
    medium_intent_sources = ['google-ads', 'facebook-ads']
    source = lead_data.get('source', 'organic')
    
    if source in high_intent_sources:
        intent_score = 20
    elif source in medium_intent_sources:
        intent_score = 15
    else:
        intent_score = 10
    
    # Readiness Score (0-25)
    readiness_score = 0
    years_in_city = lead_data.get('years_in_city', 0)
    if years_in_city >= 5:
        readiness_score += 15
    elif years_in_city >= 2:
        readiness_score += 10
    elif years_in_city >= 1:
        readiness_score += 5
    
    if enrichment_data and enrichment_data.get('credit_indicators', {}).get('has_stable_employment'):
        readiness_score += 10
    
    # Engagement Score (0-20)
    engagement_score = 20  # Assume high engagement for new leads
    
    # Total Score
    total_score = budget_score + intent_score + readiness_score + engagement_score
    
    # Determine confidence
    confidence = 'high' if enrichment_data and lead_data.get('budget') else 'medium'
    if not lead_data.get('budget') and not enrichment_data:
        confidence = 'low'
    
    # Generate insights
    strengths = []
    concerns = []
    recommendations = []
    
    if budget_score >= 20:
        strengths.append("Strong budget alignment")
    if intent_score >= 15:
        strengths.append("High purchase intent from quality source")
    if readiness_score >= 15:
        strengths.append("Stable and ready to move forward")
    
    if budget_score < 15:
        concerns.append("Budget may be insufficient")
    if not lead_data.get('phone'):
        concerns.append("No phone number provided")
    
    if total_score >= 70:
        recommendations.extend([
            "Fast-track to sales team",
            "Schedule property viewing within 48 hours",
            "Assign senior sales agent"
        ])
    elif total_score >= 50:
        recommendations.extend([
            "Nurture with targeted content",
            "Schedule discovery call",
            "Send market analysis report"
        ])
    else:
        recommendations.extend([
            "Add to long-term nurture campaign",
            "Send educational content series",
            "Re-evaluate in 3 months"
        ])
    
    reasoning = f"Lead scored {total_score}/100 with {confidence} confidence. "
    if total_score >= 70:
        reasoning += "Highly qualified lead ready for immediate sales engagement."
    elif total_score >= 50:
        reasoning += "Moderate qualification, needs nurturing before sales."
    else:
        reasoning += "Low qualification, requires long-term nurturing."
    
    # Return as dictionary for Strands compatibility
    return {
        "budget_score": budget_score,
        "intent_score": intent_score,
        "readiness_score": readiness_score,
        "engagement_score": engagement_score,
        "total_score": total_score,
        "confidence": confidence,
        "reasoning": reasoning,
        "strengths": strengths,
        "concerns": concerns,
        "recommendations": recommendations
    }


# Tool 3: Make Qualification Decision
@tool
def make_qualification_decision(
    score: Dict[str, Any],
    require_human_review_threshold: int = 65
) -> Dict[str, Any]:
    """
    Makes the final qualification decision based on the score.
    Determines status and whether human review is needed.
    """
    # Tool output is controlled by agent streaming, no need for prints
    
    # Determine status
    if score['total_score'] >= 70 and score['confidence'] == 'high':
        status = 'qualified'
    elif score['total_score'] < 40:
        status = 'not_qualified'
    else:
        status = 'needs_review'
    
    # Check if human review needed
    requires_human_review = (
        status == 'needs_review' or
        score['confidence'] == 'low' or
        (score['total_score'] >= 60 and score['total_score'] <= 70) or
        len(score['concerns']) > 2
    )
    
    human_review_reason = None
    if requires_human_review:
        if score['confidence'] == 'low':
            human_review_reason = "Low confidence due to insufficient data"
        elif status == 'needs_review':
            human_review_reason = "Borderline qualification score"
        elif len(score['concerns']) > 2:
            human_review_reason = "Multiple concerns identified"
    
    next_steps = score['recommendations'].copy()
    if requires_human_review:
        next_steps.insert(0, "Queue for human review within 4 hours")
    
    return {
        "status": status,
        "requires_human_review": requires_human_review,
        "human_review_reason": human_review_reason,
        "next_steps": next_steps,
        "qualified_at": datetime.now().isoformat(),
        "qualified_by": "strands-qualification-agent"
    }


# System prompt for the qualification agent
QUALIFICATION_SYSTEM_PROMPT = """
You are a Lead Qualification Agent for a real estate CRM system.

Your role is to evaluate leads and determine their qualification status using the available tools.

Follow this process:
1. First, enrich the lead data using the enrich_lead tool
2. Calculate the qualification score using calculate_qualification_score tool
3. Make the final decision using make_qualification_decision tool

IMPORTANT RULES:
- If a tool fails, do NOT retry it more than ONCE
- If enrichment fails, proceed with the original data
- Always complete the qualification even with partial data
- Do not get stuck in retry loops
- The tools accept lead data as a dictionary with string values for budget (e.g., "$250,000")
- Do NOT try to convert budget to integer before passing to tools

Always be objective and data-driven in your assessments. Consider both explicit data 
(budget, timeline) and implicit signals (source, engagement).

When presenting results, clearly explain the reasoning behind your qualification decision.
"""


def create_qualification_agent():
    """Creates and returns the qualification agent with all tools"""
    # Hardcode AWS region for now
    os.environ['AWS_REGION'] = 'us-east-1'
    # Optionally use a different profile
    # os.environ['AWS_PROFILE'] = 'tr-ihn-preprod'
    
    # Wrap tools to handle errors gracefully
    def safe_tool(tool_func):
        """Wrapper to prevent tool errors from crashing the agent"""
        def wrapper(*args, **kwargs):
            try:
                return tool_func(*args, **kwargs)
            except Exception as e:
                print(f"\n[WARNING] Tool error: {str(e)}")
                # Return a default response
                if tool_func.__name__ == 'enrich_lead':
                    return {"email": args[0] if args else "", "error": str(e)}
                elif tool_func.__name__ == 'calculate_qualification_score':
                    return {"total_score": 50, "confidence": "low", "error": str(e)}
                elif tool_func.__name__ == 'make_qualification_decision':
                    return {"status": "needs_review", "error": str(e)}
                return {"error": str(e)}
        wrapper.__name__ = tool_func.__name__
        wrapper.__doc__ = tool_func.__doc__
        return wrapper
    
    # Use tools directly without wrapper for now
    tools = [
        enrich_lead,
        calculate_qualification_score,
        make_qualification_decision
    ]
    
    # Use BedrockModel with Amazon Nova Lite (supports everything, very cost-effective)
    model = BedrockModel(
        model_id="amazon.nova-lite-v1:0",  # Amazon Nova Lite - $0.06/$0.24 per 1M tokens, no payment required
        temperature=0.1,  # Low temperature for consistent qualification decisions
        streaming=True  # Nova supports streaming with tools!
    )
    
    return Agent(
        system_prompt=QUALIFICATION_SYSTEM_PROMPT,
        tools=tools,
        model=model
    )


def qualify_lead(lead: LeadInput, verbose: bool = True) -> Dict:
    """Main function to qualify a lead
    
    Args:
        lead: LeadInput object with lead data
        verbose: If True, print full response. If False, print summary only.
    """
    if verbose:
        print(f"\n[START] Starting qualification for lead: {lead.email}")
        print("=" * 60)
    
    # Check AWS configuration first
    if verbose:
        print_aws_config_status()
    
    # Create agent
    agent = create_qualification_agent()
    
    # Prepare lead data for agent
    lead_dict = {
        "id": lead.id,
        "email": lead.email,
        "phone": lead.phone,
        "budget": lead.budget,
        "years_in_city": lead.years_in_city,
        "occupation": lead.occupation,
        "source": lead.source,
        "created_at": lead.created_at or datetime.now().isoformat(),
        "metadata": lead.metadata or {}
    }
    
    # Create prompt for agent
    prompt = f"""
    Please qualify this lead for our real estate CRM:
    
    Lead Information:
    {json.dumps(lead_dict, indent=2)}
    
    Use your tools to:
    1. Enrich the lead data
    2. Calculate qualification scores
    3. Make a qualification decision
    
    Provide a comprehensive analysis including the score breakdown, 
    strengths, concerns, and recommended next steps.
    """
    
    # Track timing and cost
    if verbose:
        timer = AgentTimer("Lead Qualification")
        timer.__enter__()
    
    try:
        # Run agent - agent is callable, so use agent(prompt)
        response = agent(prompt)
        
        # Estimate cost (for testing purposes)
        cost_info = calculate_cost(prompt, str(response), "amazon.nova-lite-v1:0")
        if verbose:
            print_cost_summary(cost_info)
            
    except Exception as e:
        print(f"\n[ERROR] Agent Error: {str(e)}")
        if verbose:
            print("\n[TIP] Troubleshooting tips:")
            print("   - Check AWS credentials are configured")
            print("   - Ensure Bedrock access is enabled")
            print("   - Verify Claude 3.5 Sonnet is enabled in your region")
            print("   - AWS_REGION is hardcoded to us-east-1")
        raise
        
    finally:
        if verbose and 'timer' in locals():
            timer.__exit__(None, None, None)
    
    # The response contains the agent's analysis and results
    response_str = str(response)
    
    # Extract key information
    # Try to extract qualification status
    if "NOT QUALIFIED" in response_str.upper():
        status = "NOT QUALIFIED"
    elif "QUALIFIED" in response_str.upper():
        if "NEEDS" in response_str.upper() and "REVIEW" in response_str.upper():
            status = "NEEDS REVIEW"
        else:
            status = "QUALIFIED"
    else:
        status = "NEEDS REVIEW"
        
    # Try to extract score - look for different patterns Nova uses
    import re
    score = None
    
    # Try multiple patterns to find the score
    patterns = [
        r'Total Score[:\s]*(\d+)',             # Total Score: 90
        r'Total Qualification Score[:\s]*(\d+)', # Total Qualification Score: 75
        r'total_score["\s:]+(\d+)',            # "total_score": 95
        r'scored (\d+)/100',                    # Lead scored 85/100
        r'score of (\d+)',                      # score of 85
        r'Score[:\s]*(\d+)/100',               # Score: 85/100
        r'qualification_score["\s:]+(\d+)',     # "qualification_score": 45
        r'Score:\s*(\d+)',                     # Score: 90 (from score breakdown)
    ]
    
    for pattern in patterns:
        score_match = re.search(pattern, response_str, re.IGNORECASE | re.MULTILINE)
        if score_match:
            potential_score = int(score_match.group(1))
            # Nova sometimes gives scores > 100, normalize to 100
            if potential_score > 100:
                score = min(potential_score // 10, 100)  # Likely summed sub-scores
            else:
                score = potential_score
            break
    
    # Build result dict
    result = {
        "status": status,
        "score": score,
        "response": response_str,
        "cost": cost_info.get('total_cost', 0) if 'cost_info' in locals() else 0
    }
    
    # Only print if verbose
    if verbose:
        print("\n" + "="*60)
        print("AGENT RESPONSE:")
        print("="*60)
        print(response_str)
        print()
    
    # Always print summary
    score_str = str(score) if score is not None else "N/A"
    print(f"\n[SUMMARY] Status: {status} | Score: {score_str}/100")
    
    return result


# Test function for local development
def test_qualification():
    """Test the qualification agent with sample leads"""
    
    # Test Case 1: High-quality lead
    lead1 = LeadInput(
        id="test-001",
        tenant_id="tenant-123",
        email="sarah.johnson@techstartup.com",
        phone="+1-555-987-6543",
        budget="$450,000",
        years_in_city=5,
        occupation="Product Manager",
        source="referral",
        metadata={
            "property_interest": "3-bedroom house",
            "timeline": "3-6 months"
        }
    )
    
    # Test Case 2: Low-quality lead
    lead2 = LeadInput(
        id="test-002",
        tenant_id="tenant-123",
        email="test@gmail.com",
        budget="$50,000",
        source="organic"
    )
    
    # Run tests
    for lead in [lead1, lead2]:
        print(f"\n{'='*80}")
        print(f"Testing lead: {lead.email}")
        print('='*80)
        
        try:
            result = qualify_lead(lead)
            print("\n[OK] Qualification completed successfully!")
            print(f"Result: {result}")
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Run test when script is executed directly
    test_qualification()
