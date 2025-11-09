"""
Simple example of using the Qualification Agent with Strands SDK
"""

from qualification_agent import create_qualification_agent

def main():
    """Example of using the qualification agent"""
    
    # Create the agent
    print("[AGENT] Creating Qualification Agent...")
    agent = create_qualification_agent()
    
    # Example lead data
    lead_info = """
    Please qualify this lead for our real estate CRM:
    
    Lead Information:
    - Email: sarah.johnson@techstartup.com
    - Phone: +1-555-987-6543
    - Budget: $450,000
    - Years in City: 5
    - Occupation: Product Manager
    - Source: referral
    - Property Interest: 3-bedroom house in downtown area
    - Timeline: Looking to buy in the next 3-6 months
    
    Use your tools to analyze this lead and provide a qualification decision.
    """
    
    print("\n📋 Processing lead...")
    print("="*60)
    
    try:
        # Run the agent - agent is callable
        response = agent(lead_info)
        
        print("\n[OK] Qualification Complete!")
        print("="*60)
        print("\nAgent Analysis:")
        print(response)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Note: This requires AWS credentials configured for Bedrock access
    # Set AWS_PROFILE or AWS access keys before running
    main()
