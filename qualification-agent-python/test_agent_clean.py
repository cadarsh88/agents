"""
Clean test runner for the Qualification Agent
Shows only essential information in a clean format
"""

from qualification_agent import LeadInput, qualify_lead
from utils import print_aws_config_status
import sys
import os
from contextlib import redirect_stdout
import io
import re


def capture_qualification(lead: LeadInput) -> tuple[str, dict]:
    """Capture the qualification output and extract key info"""
    # Capture all output
    buffer = io.StringIO()
    
    # Redirect stdout to capture output
    with redirect_stdout(buffer):
        try:
            result = qualify_lead(lead, verbose=False)
        except Exception as e:
            return f"Error: {str(e)}", {"status": "error", "error": str(e)}
    
    # Get the printed output
    output = buffer.getvalue()
    
    # Use the structured result returned by qualify_lead
    if isinstance(result, dict):
        status = result.get("status", "Unknown")
        score = result.get("score")
        score_str = str(score) if score is not None else "N/A"
        
        return output, {"status": status, "score": score_str}
    else:
        # Fallback to parsing the output if not a dict
        return output, {"status": "Unknown", "score": "N/A"}


def test_single_lead_clean():
    """Test with a single lead - clean output"""
    print("\n" + "="*60)
    print(" QUALIFICATION AGENT TEST - Single Lead")
    print("="*60)
    
    lead = LeadInput(
        id="test-001",
        tenant_id="tenant-123",
        email="sarah.johnson@techcorp.com",
        phone="+1-555-987-6543",
        budget="$450,000",
        years_in_city=5,
        occupation="Senior Product Manager",
        source="referral",
        metadata={
            "property_interest": "3-4 bedroom house",
            "timeline": "3-6 months",
            "pre_approved": "yes",
            "current_residence": "renting",
            "family_size": "4"
        }
    )
    
    print(f"\nTesting: {lead.occupation} ({lead.email})")
    print(f"Budget: {lead.budget} | Source: {lead.source}")
    
    output, info = capture_qualification(lead)
    
    print(f"\n[OK] Status: {info['status']} | Score: {info['score']}/100")
    print("\n[SUCCESS] Test completed")


def test_multiple_clean():
    """Test multiple scenarios with clean output"""
    print("\n" + "="*60)
    print(" QUALIFICATION AGENT TEST - Multiple Scenarios")
    print("="*60)
    
    test_leads = [
        {
            "name": "High-Value Executive",
            "lead": LeadInput(
                id="test-luxury",
                tenant_id="tenant-123",
                email="ceo@fortune500.com",
                phone="+1-555-111-2222",
                budget="$1,200,000",
                years_in_city=8,
                occupation="Chief Executive Officer",
                source="direct",
                metadata={
                    "property_interest": "Luxury penthouse or estate",
                    "timeline": "immediate",
                    "cash_buyer": "yes"
                }
            )
        },
        {
            "name": "First-Time Buyer",
            "lead": LeadInput(
                id="test-firsttime",
                tenant_id="tenant-123",
                email="young.professional@gmail.com",
                phone="+1-555-333-4444",
                budget="$250,000",
                years_in_city=2,
                occupation="Junior Developer",
                source="google-ads",
                metadata={
                    "property_interest": "Condo or starter home",
                    "timeline": "6-12 months",
                    "first_time_buyer": "yes"
                }
            )
        },
        {
            "name": "Unqualified Lead",
            "lead": LeadInput(
                id="test-unqualified",
                tenant_id="tenant-123",
                email="browsing@yahoo.com",
                budget="$50,000",
                source="organic",
                metadata={
                    "just_browsing": "yes"
                }
            )
        }
    ]
    
    # First check AWS config once
    print("\nChecking AWS Configuration...")
    print_aws_config_status()
    
    print("\n" + "-"*60)
    print(" Running qualification tests...")
    print("-"*60)
    
    results = []
    total_cost = 0
    
    for i, scenario in enumerate(test_leads, 1):
        lead = scenario['lead']
        print(f"\n[{i}/3] {scenario['name']}")
        print(f"     Email: {lead.email}")
        print(f"     Budget: {lead.budget}")
        
        # Suppress tool warnings by redirecting stderr
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        try:
            output, info = capture_qualification(lead)
            
            # Extract cost if available
            cost_match = re.search(r'TOTAL COST:\s*\$(\d+\.\d+)', output)
            if cost_match:
                total_cost += float(cost_match.group(1))
            
            status_icon = "[OK]" if "QUALIFIED" in info['status'] and "NOT" not in info['status'] else "[X]"
            print(f"     {status_icon} Status: {info['status']} | Score: {info['score']}/100")
            
            results.append({
                "scenario": scenario['name'],
                "status": info['status'],
                "score": info['score'],
                "qualified": "NOT" not in info['status']
            })
        finally:
            sys.stderr = old_stderr
    
    # Summary
    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    
    qualified_count = len([r for r in results if r['qualified']])
    print(f"\nQualification Results:")
    for r in results:
        status_icon = "[OK]" if r['qualified'] else "[X]"
        print(f"  {status_icon} {r['scenario']}: {r['status']} (Score: {r['score']})")
    
    print(f"\nTotal: {qualified_count}/{len(results)} qualified")
    print(f"Total cost: ${total_cost:.6f}")
    
    return qualified_count == 2  # Expecting 2 qualified, 1 not qualified


def main():
    """Main test runner"""
    print("\n[CLEAN] QUALIFICATION AGENT TEST")
    print("Testing lead qualification with minimal output\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            test_single_lead_clean()
        elif sys.argv[1] == "multi":
            success = test_multiple_clean()
            if success:
                print("\n[SUCCESS] All tests passed as expected!")
            else:
                print("\n[WARNING] Unexpected results")
        else:
            print("Usage: python test_agent_clean.py [single|multi]")
    else:
        # Default: run multi test
        test_multiple_clean()


if __name__ == "__main__":
    # Suppress the annoying tool wrapper warnings
    import warnings
    warnings.filterwarnings("ignore")
    
    main()
