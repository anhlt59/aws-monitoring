# AI-Powered Log Analysis Feature

## Overview

The AI-powered log analysis feature enhances the AWS monitoring system by automatically analyzing error logs using OpenAI GPT models. It identifies patterns, categorizes issues, determines severity levels, and provides actionable solutions for troubleshooting.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Master Stack (10-minute cycle)              │
│                                                                 │
│  ┌──────────────┐     ┌──────────────────┐    ┌──────────────┐│
│  │  EventBridge │────▶│ AILogAnalysis    │───▶│  DynamoDB    ││
│  │   Schedule   │     │     Lambda       │    │  - Context   ││
│  │  (10 min)    │     │                  │    │  - Analysis  ││
│  └──────────────┘     └──────────────────┘    │  - Events    ││
│                              │                 └──────────────┘│
│                              │                                  │
│                              ▼                                  │
│                       ┌──────────────┐                         │
│                       │  OpenAI API  │                         │
│                       │   GPT-4o     │                         │
│                       └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### Processing Pipeline

1. **Event Collection** (Every 10 minutes)
   - Query events from the last 10 minutes
   - Extract log messages from event details

2. **Pre-processing**
   - **Deduplication**: Remove logs with >85% similarity
   - **Sanitization**: Remove sensitive data (AWS keys, IPs, emails, etc.)

3. **AI Analysis**
   - Load system context from database
   - Send deduplicated, sanitized logs to OpenAI
   - Receive structured analysis results

4. **Storage & Deduplication**
   - Check for existing analysis (same day, same pattern)
   - If exists: Increment frequency counter
   - If new: Create new analysis record
   - Link events to analysis results

## Database Schema

### 1. Context Table

Stores system context information to help AI understand the architecture and technology stack.

**Schema:**
```
pk: "CONTEXT"
sk: "CONTEXT#{context_type}#{context_id}"
```

**Fields:**
- `context_type`: Type of context (backend/database/api/architecture/infrastructure)
- `title`: Human-readable title
- `content`: JSON with detailed context information
- `version`: Version for tracking updates
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Example:**
```json
{
  "id": "backend-architecture",
  "context_type": "backend",
  "title": "AWS Lambda Backend Architecture",
  "content": {
    "runtime": "Python 3.13",
    "framework": "Serverless Framework 4.x",
    "database": "DynamoDB",
    "architecture": "Hexagonal (Ports and Adapters)"
  },
  "version": "1.0"
}
```

### 2. Log Analysis Table

Stores AI analysis results with deduplication based on patterns and date.

**Schema:**
```
pk: "LOG_ANALYSIS"
sk: "LOG_ANALYSIS#{date}#{analysis_hash}"
```

**Fields:**
- `date`: YYYY-MM-DD format for daily grouping
- `analysis_hash`: Hash of patterns/categories for deduplication
- `context_ids`: Links to relevant context schemas
- `severity`: 0=Unknown, 1=Low, 2=Medium, 3=High, 4=Critical
- `categories`: List of issue categories (e.g., ["Database", "Connection"])
- `patterns`: Identified log patterns
- `frequency`: Count of similar occurrences in the same day
- `summary`: Concise summary of the issue
- `solution`: Recommended solution or action
- `log_sample`: Sample log entry for reference
- `event_ids`: Links to related event IDs
- `account`: AWS Account ID
- `region`: AWS Region
- `analyzed_at`: Analysis timestamp
- `updated_at`: Last update timestamp

**Example:**
```json
{
  "id": "abc123def456",
  "date": "2025-01-15",
  "severity": 3,
  "categories": ["Database", "Connection", "Timeout"],
  "patterns": [
    "Connection timeout after 30 seconds",
    "Failed to connect to RDS instance"
  ],
  "frequency": 15,
  "summary": "Multiple database connection timeout errors occurring during peak hours...",
  "solution": "Increase connection pool size or review query performance...",
  "log_sample": "Error: Connection timeout to db-prod-01.amazonaws.com",
  "account": "123456789012",
  "region": "us-east-1"
}
```

### 3. Events Table (Updated)

Added `analysis_id` field to link events to analysis results.

**New Field:**
- `analysis_id`: Link to LogAnalysis record (nullable)

## Configuration

### Environment Variables

Set these in `infra/master/configs/{stage}.yml`:

```yaml
AILogAnalysis:
  OpenAIApiKey: ${env:OPENAI_API_KEY}  # Required
  OpenAIModel: "gpt-4o-mini"           # Default model
  LookbackMinutes: 10                  # Query window
  SimilarityThreshold: 0.85            # 85% similarity for duplicates
  MaxLogsPerBatch: 100                 # Max logs per AI call
```

### Required Secrets

Set `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

## Key Features

### 1. Duplicate Detection (>85% Similarity)

Uses `difflib.SequenceMatcher` for fast similarity calculation without external dependencies.

**Algorithm:**
- Normalize whitespace
- Calculate similarity ratio (0.0 - 1.0)
- Logs with ≥85% similarity are considered duplicates
- Only the first occurrence is sent to AI

**Example:**
```python
# These are considered duplicates (>85% similar):
log1 = "Error: Connection timeout at 10:30:45"
log2 = "Error: Connection timeout at 10:30:46"

# Result: Only log1 is analyzed
```

### 2. Sensitive Data Removal

Automatically removes sensitive information before sending to AI:

**Protected Patterns:**
- AWS Access Keys (AKIA..., ASIA...)
- AWS Secret Keys
- IPv4 and IPv6 addresses
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers
- API keys and tokens
- JWT tokens
- Passwords in common formats
- Database connection strings

**Example:**
```python
# Before sanitization:
"User john@example.com connected from 192.168.1.100 with key AKIAIOSFODNN7EXAMPLE"

# After sanitization:
"User [EMAIL] connected from [IP_ADDRESS] with key [AWS_ACCESS_KEY]"
```

### 3. Daily Deduplication

Within the same day, identical issues are not re-analyzed:
- Pattern hash is computed from categories and patterns
- If same hash exists for today → increment frequency
- If new hash → create new analysis

This prevents redundant AI API calls and costs.

### 4. Context-Aware Analysis

AI receives system context for better understanding:
- Backend architecture
- Database schema
- API structure
- Technology stack
- Deployment configuration

## Usage

### Lambda Function

**Trigger:** EventBridge schedule (every 10 minutes)

**Location:** `src/entrypoints/functions/ai_log_analysis/main.py`

**Process:**
1. Invoked by EventBridge schedule
2. Queries events from last 10 minutes
3. Deduplicates and sanitizes logs
4. Calls OpenAI API
5. Stores/updates analysis results
6. Links events to analysis

### Repositories

**Context Repository:**
```python
from src.adapters.db.repositories import ContextRepository

repo = ContextRepository()

# Create context
context = Context(
    id="backend-architecture",
    context_type="backend",
    title="AWS Lambda Backend",
    content={"runtime": "Python 3.13", ...},
)
repo.create(context)

# List contexts
contexts = repo.list(ListContextsDTO(context_type="backend"))
```

**Log Analysis Repository:**
```python
from src.adapters.db.repositories import LogAnalysisRepository

repo = LogAnalysisRepository()

# Get existing analysis
analysis = repo.get_by_date_and_hash("2025-01-15", "abc123")

# Create new analysis
analysis = LogAnalysis(
    id="abc123",
    date="2025-01-15",
    severity=3,
    categories=["Database", "Connection"],
    ...
)
repo.create(analysis)

# Increment frequency for duplicate
repo.increment_frequency("2025-01-15", "abc123", event_ids=["evt-1", "evt-2"])
```

### OpenAI Adapter

**Location:** `src/adapters/ai/openai_analyzer.py`

**Usage:**
```python
from src.adapters.ai import OpenAILogAnalyzer

analyzer = OpenAILogAnalyzer(
    api_key="sk-...",
    model="gpt-4o-mini",
    temperature=0.3
)

result = analyzer.analyze_logs(
    logs=["Error: Connection timeout", ...],
    context="Analyzing production errors",
    system_context={"backend": "Python 3.13", ...}
)

print(result.severity)     # 3
print(result.categories)   # ["Database", "Connection"]
print(result.summary)      # "Multiple timeout errors..."
print(result.solution)     # "Increase connection pool..."
```

## Cost Optimization

### Token Usage

- **Model:** gpt-4o-mini (cost-efficient)
- **Input:** ~500-2000 tokens (logs + context)
- **Output:** ~200-500 tokens (analysis)
- **Cost:** ~$0.001-0.005 per analysis

### Optimization Strategies

1. **Deduplication:** Reduces API calls by ~70-90%
2. **Daily caching:** Same issue analyzed only once per day
3. **Batch size limit:** Max 100 logs per call
4. **Efficient model:** gpt-4o-mini vs gpt-4

**Estimated Monthly Cost:**
- 10-minute frequency: 144 calls/day
- ~50% actually trigger analysis: 72 calls/day
- Daily deduplication: ~20-30 unique analyses/day
- **Total:** ~$5-15/month

## Testing

### Unit Tests

**Text Similarity:**
```bash
poetry run pytest tests/common/test_text_similarity.py -v
```

**Sanitization:**
```bash
poetry run pytest tests/common/test_sanitization.py -v
```

**All tests:**
```bash
make test
```

### Test Coverage

Current coverage for new utilities:
- `text_similarity.py`: 100%
- `sanitization.py`: 100%

## Deployment

### Prerequisites

1. Set OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. Update dependencies:
   ```bash
   poetry install
   poetry lock
   ```

### Deploy to LocalStack

```bash
make deploy-local
```

### Deploy to Production

```bash
# Deploy to staging (cm)
make deploy-cm

# Deploy to production (neos)
make deploy-neos
```

## Monitoring

### CloudWatch Metrics

- **Lambda Invocations:** AILogAnalysis function
- **Duration:** Average processing time
- **Errors:** Failed analyses
- **Throttles:** Rate limit issues

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/lambda/monitoring-master-{stage}-AILogAnalysis --follow
```

### Key Metrics

- Events processed per run
- Logs deduplicated (%)
- AI analysis success rate
- Average analysis time
- Cost per analysis

## Troubleshooting

### Common Issues

**1. OpenAI API Key Not Set**
```
Error: OpenAI API key is required
```
**Solution:** Set `OPENAI_API_KEY` environment variable

**2. Rate Limit Exceeded**
```
Error: Rate limit reached
```
**Solution:** Reduce frequency or upgrade OpenAI plan

**3. No Events Found**
```
Info: No events found in the specified time range
```
**Solution:** Normal behavior when no events exist

**4. Analysis Failed**
```
Error: OpenAI log analysis failed
```
**Solution:** Check logs for details, fallback result is returned

### Debug Mode

Enable debug logging:
```yaml
Lambda:
  Environment:
    LOG_LEVEL: DEBUG
```

## Future Enhancements

1. **Real-time Analysis:** Analyze high-severity events immediately
2. **Trend Detection:** Identify increasing error patterns over time
3. **Auto-remediation:** Trigger automated fixes for known issues
4. **Slack Notifications:** Send analysis summaries to Slack
5. **Dashboard:** Visualize analysis trends and insights
6. **Custom Models:** Fine-tune models for specific error patterns
7. **Multi-account Support:** Analyze logs across multiple AWS accounts

## Security Considerations

### Data Privacy

- All sensitive data is removed before sending to AI
- Logs are encrypted in transit (HTTPS/TLS 1.2+)
- DynamoDB tables encrypted at rest (AWS KMS)

### API Key Security

- Never commit API keys to version control
- Use environment variables or AWS Secrets Manager
- Rotate keys regularly
- Monitor API usage for anomalies

### Access Control

- Lambda execution role has minimal required permissions
- Context and analysis tables use IAM policies
- API access restricted by resource-based policies

## Compliance

- **GDPR:** Sensitive data removed before processing
- **PCI-DSS:** Credit card patterns sanitized
- **HIPAA:** No PHI sent to external APIs
- **SOC 2:** Audit logs maintained for all analyses
