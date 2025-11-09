"""
Mock Qualification Agent for testing without AWS/Bedrock
Simulates the agent behavior using just the tools directly
"""

from qualification_agent import (
    LeadInput, 
    enrich_lead, 
    calculate_qualification_score, 
    make_qualification_decision,
    QUALIFICATION_SYSTEM_PROMPT
)
from utils import AgentTimer, calculate_cost, print_cost_summary
import json


class MockQualificationAgent:
    """Mock agent that simulates Strands Agent behavior"""
    
    def __init__(self):
        self.system_prompt = QUALIFICATION_SYSTEM_PROMPT
        self.tools = {
            "enrich_lead": enrich_lead,
            "calculate_qualification_score": calculate_qualification_score,
            "make_qualification_decision": make_qualification_decision
        }
    
    def qualify(self, lead: LeadInput) -> str:
        """Simulate agent qualification process"""
        
        print("\n[MOCK] Mock Agent Processing (No AWS Required)...")
        print("="*60)
        
        # Simulate agent thinking
        print("\n[AGENT] I'll help you qualify this lead. Let me analyze the information step by step.")
        
        lead_dict = {
            "id": lead.id,
            "email": lead.email,
            "phone": lead.phone,
            "budget": lead.budget,
            "years_in_city": lead.years_in_city,
            "occupation": lead.occupation,
            "source": lead.source,
            "metadata": lead.metadata or {}
        }
        
        # Step 1: Enrichment
        print("\n[STEP 1] Enriching lead data...")
        enrichment = enrich_lead(lead.email, lead.phone)
        print(f"   [OK] Found company: {enrichment.get('company_info', {}).get('name', 'N/A')}")
        print(f"   [OK] Estimated income: {enrichment.get('estimated_income', 'Unknown')}")
        
        # Step 2: Scoring
        print("\n[STEP 2] Calculating qualification score...")
        score = calculate_qualification_score(lead_dict, enrichment)
        print(f"   [OK] Total Score: {score['total_score']}/100")
        print(f"   [OK] Confidence: {score['confidence']}")
        
        # Step 3: Decision
        print("\n[STEP 3] Making qualification decision...")
        decision = make_qualification_decision(score)
        print(f"   [OK] Status: {decision['status'].upper()}")
        print(f"   [OK] Human Review: {'Required' if decision['requires_human_review'] else 'Not Required'}")
        
        # Generate response like the real agent would
        response = f"""
Based on my analysis of the lead {lead.email}, here are my findings:

**Lead Information:**
- Email: {lead.email}
- Budget: {lead.budget or 'Not provided'}
- Source: {lead.source}
- Years in City: {lead.years_in_city or 'Not provided'}
- Occupation: {lead.occupation or 'Not provided'}

**Enrichment Results:**
- Company: {enrichment.get('company_info', {}).get('name', 'Personal email')}
- Estimated Income: {enrichment.get('estimated_income', 'Unknown')}
- Employment Stability: {'Yes' if enrichment.get('credit_indicators', {}).get('has_stable_employment') else 'Unknown'}

**Qualification Score Breakdown:**
- Budget Score: {score['budget_score']}/30
- Intent Score: {score['intent_score']}/25
- Readiness Score: {score['readiness_score']}/25
- Engagement Score: {score['engagement_score']}/20
- **Total Score: {score['total_score']}/100** ({score['confidence']} confidence)

**Analysis:**
{score['reasoning']}

**Strengths:**
{chr(10).join(f'- {s}' for s in score['strengths']) if score['strengths'] else '- No specific strengths identified'}

**Concerns:**
{chr(10).join(f'- {c}' for c in score['concerns']) if score['concerns'] else '- No major concerns'}

**Decision: {decision['status'].upper()}**
{f'Note: {decision["human_review_reason"]}' if decision.get('human_review_reason') else ''}

**Recommended Next Steps:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(decision['next_steps']))}

This qualification was completed using a mock agent for testing purposes.
"""
        
        return response


def test_mock_agent():
    """Test the mock agent with a sample lead"""
    
    print("\n[TEST] Testing Mock Qualification Agent")
    print("This runs without AWS/Bedrock access\n")
    
    # Create test lead
    lead = LeadInput(
        id="mock-test-001",
        tenant_id="tenant-123",
        email="john.smith@techstartup.com",
        phone="+1-555-1234",
        budget="$350,000",
        years_in_city=4,
        occupation="Software Engineer",
        source="referral",
        metadata={
            "property_interest": "3-bedroom house",
            "timeline": "3-6 months"
        }
    )
    
    # Create mock agent
    agent = MockQualificationAgent()
    
    # Track timing
    with AgentTimer("Mock Qualification"):
        # Qualify lead
        response = agent.qualify(lead)
        
        # Estimate cost
        prompt = f"Qualify lead: {json.dumps(lead.__dict__, default=str)}"
        cost_info = calculate_cost(prompt, response)
        print_cost_summary(cost_info)
    
    # Print results
    print("\n" + "="*60)
    print("MOCK AGENT RESPONSE:")
    print("="*60)
    print(response)
    
    print("\n[OK] Mock test completed successfully!")
    print("[TIP] This demonstrates the qualification logic without requiring AWS access.")


if __name__ == "__main__":
    test_mock_agent()
