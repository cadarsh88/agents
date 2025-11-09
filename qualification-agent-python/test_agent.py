"""
Easy test script for the Qualification Agent
Run this to test the agent with pre-configured leads
"""

from qualification_agent import LeadInput, qualify_lead
from utils import print_aws_config_status
import sys


def test_single_lead():
    """Test with a single well-defined lead"""
    
    print("\n" + "="*80)
    print(" QUALIFICATION AGENT TEST - Single Lead")
    print("="*80)
    
    # High-quality test lead
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
    
    try:
        result = qualify_lead(lead)
        print("\n[OK] Test completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        return False
    
    return True


def test_multiple_scenarios():
    """Test with multiple lead scenarios"""
    
    print("\n" + "="*80)
    print(" QUALIFICATION AGENT TEST - Multiple Scenarios")
    print("="*80)
    
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
    
    results = []
    
    for scenario in test_leads:
        print(f"\n\n{'='*60}")
        print(f" Testing: {scenario['name']}")
        print('='*60)
        
        try:
            # Use verbose=False for multi-scenario testing
            result = qualify_lead(scenario['lead'], verbose=False)
            results.append({
                "scenario": scenario['name'],
                "status": "Success",
                "lead_id": scenario['lead'].id
            })
        except Exception as e:
            results.append({
                "scenario": scenario['name'],
                "status": "Failed",
                "error": str(e)
            })
            print(f"\n[ERROR] Scenario failed: {str(e)}")
    
    # Summary
    print("\n\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)
    for result in results:
        status_icon = "[OK]" if result["status"] == "Success" else "[FAIL]"
        print(f"{status_icon} {result['scenario']}: {result['status']}")
    
    success_count = len([r for r in results if r["status"] == "Success"])
    print(f"\nTotal: {success_count}/{len(results)} tests passed")
    
    return success_count == len(results)


def main():
    """Main test runner"""
    
    print("\n[BOT] QUALIFICATION AGENT TEST SUITE")
    print("Testing lead qualification with AWS Strands Agents\n")
    
    # Check if user wants to run specific test
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            success = test_single_lead()
        elif sys.argv[1] == "multi":
            success = test_multiple_scenarios()
        else:
            print("Usage: python test_agent.py [single|multi]")
            print("  single - Test with one detailed lead")
            print("  multi  - Test with multiple scenarios")
            return
    else:
        # Default: run single test
        success = test_single_lead()
    
    if success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
