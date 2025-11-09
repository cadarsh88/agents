# Lead Qualification Agent - Python Implementation

This is a Python implementation of the Lead Qualification Agent using AWS Strands Agents SDK.

## Features

- **Model-driven approach**: Uses Strands Agents for orchestration
- **Multi-factor scoring**: Budget, Intent, Readiness, and Engagement
- **Lead enrichment**: Mock enrichment (replace with real APIs in production)
- **Human-in-the-loop**: Automatic escalation for edge cases
- **Local testing**: Test without AWS credentials first

## Project Structure

```
qualification-agent-python/
├── qualification_agent.py   # Main agent implementation
├── test_local.py           # Local test without Strands SDK
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

1. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   - Ensure your AWS credentials are configured
   - You need access to Amazon Bedrock in us-west-2
   - Enable access to Claude 3.5 Sonnet in Bedrock console

## Testing Options

### 1. Mock Agent (No AWS Required) ⭐ Recommended for first test
```bash
# Simulates the full agent without needing AWS credentials
python mock_agent.py
```

### 2. Local Logic Test (No AWS Required)
```bash
# Tests just the qualification logic
python test_local.py
```

### 3. Quick Agent Test (Requires AWS)
```bash
# Test with a single pre-configured lead
python test_agent.py single

# Test with multiple scenarios
python test_agent.py multi
```

### 4. Full Agent Test (Requires AWS Bedrock)
Run the complete agent with example leads:
   ```bash
   python example_usage.py
   ```

2. **Run the full test suite**:
   ```bash
   python qualification_agent.py
   ```

3. **What happens**:
   - Agent uses Claude 3.5 Sonnet via Bedrock
   - Enriches lead data (mock for now)
   - Calculates qualification score
   - Makes qualification decision
   - Provides detailed analysis

## How It Works

1. **Lead Input**: Receives lead data (email, budget, source, etc.)

2. **Enrichment**: 
   - Enriches lead with additional data
   - Mock implementation for testing
   - Replace with Clearbit/PeopleDataLabs in production

3. **Scoring** (0-100 points):
   - Budget Score (0-30): Based on budget amount
   - Intent Score (0-25): Based on lead source
   - Readiness Score (0-25): Years in city + employment
   - Engagement Score (0-20): Response time

4. **Decision**:
   - Qualified: Score ≥ 70 with high confidence
   - Not Qualified: Score < 40
   - Needs Review: Score 40-70 or low confidence

5. **Human Review**: Triggered for:
   - Edge cases (score 60-70)
   - Low confidence
   - Multiple concerns
   - Missing critical data

## Customization

### Change Scoring Weights

Edit the scoring logic in `calculate_qualification_score()`:

```python
# Adjust these thresholds
if budget_num >= 500000:
    budget_score += 20  # Change weight here
```

### Add Real Enrichment

Replace the mock enrichment in `enrich_lead()`:

```python
# Add your API calls here
response = requests.get(f"https://api.clearbit.com/v2/people/find?email={email}")
```

### Use Different Models

Change the model in `create_qualification_agent()`:

```python
# For cheaper option - Claude 3 Haiku
model = BedrockModel(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region="us-west-2"
)

# For Amazon Nova models (when available)
model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    region="us-west-2"
)

# For other providers (via Strands)
from strands.models.openai import OpenAIModel
model = OpenAIModel(api_key="your-key", model_id="gpt-4")
```

## Production Deployment

1. **Add real enrichment APIs**
2. **Store results in database**
3. **Add comprehensive logging**
4. **Set up as Lambda function**
5. **Connect to EventBridge**
6. **Add monitoring/alerts**

## Cost Optimization

- Default: Claude 3.5 Sonnet
- For testing: Use Claude 3 Haiku (cheaper)
- For high-value leads: Upgrade to Claude 3 Opus
- Monitor token usage in production

## Next Steps

1. Test locally with `test_local.py`
2. Install Strands and test with real agent
3. Customize scoring for your business
4. Add real enrichment APIs
5. Deploy to AWS Lambda
