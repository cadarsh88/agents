"""
Local test script for qualification logic (without Strands SDK)
Run this first to test the scoring logic before using the full agent
"""

from qualification_agent import (
    LeadInput, 
    enrich_lead, 
    calculate_qualification_score,
    make_qualification_decision
)
from datetime import datetime
import json


def test_qualification_logic():
    """Test the qualification logic without requiring Strands SDK"""
    
    print("[TEST] Testing Qualification Logic (Local)\n")
    print("="*80)
    
    # Test leads
    test_leads = [
        # High-quality lead
        LeadInput(
            id="test-001",
            tenant_id="tenant-123",
            email="executive@fortune500.com",
            phone="+1-555-111-2222",
            budget="$750,000",
            years_in_city=10,
            occupation="Chief Technology Officer",
            source="referral",
            metadata={
                "referred_by": "John Smith (existing client)",
                "property_interest": "Luxury penthouse",
                "timeline": "immediate"
            }
        ),
        # Medium-quality lead
        LeadInput(
            id="test-002",
            tenant_id="tenant-123",
            email="freelancer@gmail.com",
            phone="+1-555-333-4444",
            budget="$200,000",
            years_in_city=2,
            occupation="Freelance Designer",
            source="google-ads",
            metadata={
                "property_interest": "Studio or 1-bedroom",
                "timeline": "6 months"
            }
        ),
        # Low-quality lead
        LeadInput(
            id="test-003",
            tenant_id="tenant-123",
            email="student123@yahoo.com",
            budget="$50,000",
            years_in_city=0,
            source="organic",
            metadata={}
        )
    ]
    
    for lead in test_leads:
        print(f"\n{'='*60}")
        print(f"Testing Lead: {lead.email}")
        print(f"Budget: {lead.budget or 'Not provided'}")
        print(f"Source: {lead.source}")
        print(f"Years in City: {lead.years_in_city or 'Not provided'}")
        print("-"*60)
        
        try:
            # Step 1: Enrich lead
            print("\n[1] Enrichment:")
            enrichment = enrich_lead(lead.email, lead.phone)
            print(f"   Company: {enrichment.get('company_info', {}).get('name', 'N/A')}")
            print(f"   Est. Income: {enrichment.get('estimated_income', 'Unknown')}")
            print(f"   Stable Employment: {enrichment.get('credit_indicators', {}).get('has_stable_employment', False)}")
            
            # Step 2: Calculate score
            print("\n[2] Scoring:")
            lead_dict = {
                'email': lead.email,
                'phone': lead.phone,
                'budget': lead.budget,
                'years_in_city': lead.years_in_city,
                'occupation': lead.occupation,
                'source': lead.source,
                'metadata': lead.metadata
            }
            
            score = calculate_qualification_score(lead_dict, enrichment)
            print(f"   Budget Score: {score['budget_score']}/30")
            print(f"   Intent Score: {score['intent_score']}/25")
            print(f"   Readiness Score: {score['readiness_score']}/25")
            print(f"   Engagement Score: {score['engagement_score']}/20")
            print(f"   TOTAL: {score['total_score']}/100 ({score['confidence']} confidence)")
            
            # Step 3: Make decision
            print("\n[3] Decision:")
            decision = make_qualification_decision(score)
            print(f"   Status: {decision['status'].upper()}")
            print(f"   Human Review: {'Yes' if decision['requires_human_review'] else 'No'}")
            if decision['human_review_reason']:
                print(f"   Review Reason: {decision['human_review_reason']}")
            
            print("\n[4] Analysis:")
            print(f"   {score['reasoning']}")
            
            if score['strengths']:
                print("\n   [STRENGTHS]:")
                for strength in score['strengths']:
                    print(f"      - {strength}")
            
            if score['concerns']:
                print("\n   [CONCERNS]:")
                for concern in score['concerns']:
                    print(f"      - {concern}")
            
            print("\n   [NEXT STEPS]:")
            for step in decision['next_steps']:
                print(f"      > {step}")
                
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("[OK] Local testing completed!")


if __name__ == "__main__":
    test_qualification_logic()
