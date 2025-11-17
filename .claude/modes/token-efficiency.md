# Token Efficiency Mode

Optimize context usage and minimize token consumption while maintaining quality.

## Mode Characteristics

- **Concise communication** - Clear but brief responses
- **Strategic tool usage** - Minimize unnecessary tool calls
- **Focused analysis** - Analyze only what's needed
- **Smart caching** - Reference instead of repeating
- **Efficient exploration** - Target searches, avoid broad scans

## When to Use

- Large codebase exploration
- Limited context budget
- Quick iterations needed
- Simple, focused tasks
- Prototype development
- Incremental changes

## Mode Behavior

### Communication Style

**Standard Mode:**
```
I'll help you implement event filtering by severity. This is a great
feature that will allow users to filter monitoring events based on
their importance level. Let me break this down into steps...

[Detailed explanation of approach]
[Full context about architecture]
[Comprehensive examples]
```

**Token Efficient Mode:**
```
Adding severity filtering:

1. Domain model: Add severity field
2. Database: Update model + mapper
3. Repository: Add filter parameter
4. API: Accept severity param
5. Tests: Cover all cases

Starting with domain model...
```

### Tool Usage Optimization

#### 1. Targeted Search
```python
# ❌ Inefficient
Glob("**/*")  # Returns everything
Grep(".*", output_mode="content")  # Too broad

# ✅ Efficient
Glob("src/domain/models/event.py")  # Specific target
Grep("class Event", output_mode="files_with_matches")  # Minimal output
```

#### 2. Minimal Reads
```python
# ❌ Inefficient
Read(file, offset=0)  # Read entire large file
Read(file1)
Read(file2)
Read(file3)  # Sequential when not all needed

# ✅ Efficient
Read(file, offset=100, limit=50)  # Read only needed lines
Read(file1)  # Only if actually needed
```

#### 3. Smart Grep
```python
# ❌ Inefficient
Grep("pattern", output_mode="content", -A=10, -B=10)  # Lots of context

# ✅ Efficient
Grep("pattern", output_mode="files_with_matches")  # Just locations
# Then Read specific files if needed
```

#### 4. Batch Operations
```python
# ❌ Inefficient
for file in files:
    Read(file)
    Analyze
    Edit(file)

# ✅ Efficient
Read all needed files in parallel
Analyze together
Edit all in parallel
```

### Analysis Optimization

#### Focus on Essentials
```python
# ❌ Verbose
"""
The Event class is a Pydantic model that represents a monitoring event
in the system. It contains multiple fields including id, account, region,
source, detail, detail_type, severity, resources, published_at, and
updated_at. The model uses Pydantic validators to ensure data integrity...
"""

# ✅ Concise
"""
Event model: id, account, region, source, detail, severity, timestamps.
Pydantic validation enforced.
"""
```

#### Skip Obvious Details
```python
# ❌ Verbose
"""
First, I'll read the file. Then I'll analyze its contents. After that,
I'll make the necessary changes. Finally, I'll verify the changes are
correct.
"""

# ✅ Concise
"""
Reading event.py, adding severity field with validation.
"""
```

### Code Examples

#### Minimal But Complete
```python
# ❌ Verbose example
"""
Here's how to add the severity field:

from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Event(BaseModel):
    # ... existing fields ...
    severity: int = Field(
        default=0,
        ge=0,
        le=4,
        description="Event severity level"
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: int) -> int:
        if not 0 <= value <= 4:
            raise ValueError("Severity must be 0-4")
        return value
"""

# ✅ Concise example
"""
Add to Event model:
severity: int = Field(default=0, ge=0, le=4)
Pydantic handles 0-4 validation automatically.
"""
```

## Optimization Techniques

### 1. Reference Don't Repeat
```python
# ❌ Repeat context
"As mentioned in CLAUDE.md, we follow hexagonal architecture.
As stated in the overview, we use DynamoDB. As documented..."

# ✅ Reference
"Following project patterns (see CLAUDE.md): domain → ports → adapters"
```

### 2. Batch Context Gathering
```python
# ❌ Sequential discovery
Grep("Event")
# Analyze
Grep("Repository")
# Analyze
Grep("Mapper")
# Analyze

# ✅ Parallel discovery
Parallel: Grep("Event"), Grep("Repository"), Grep("Mapper")
# Analyze all together
```

### 3. Progressive Detail
```python
# ❌ Full detail upfront
Read entire file
Analyze everything
Present all findings

# ✅ Progressive
Grep to locate
Read specific sections
Analyze focused area
```

### 4. Use Task Tool for Exploration
```python
# ❌ Manual exploration (many tool calls)
Glob → Grep → Read → Grep → Read → Grep → Read...

# ✅ Delegate to Task tool
Task(subagent_type="Explore", prompt="Find all event handling patterns")
```

## Token Budget Allocation

### Small Tasks (<10k tokens)
- Minimal explanation
- Direct implementation
- Essential code only
- Brief verification

### Medium Tasks (10-30k tokens)
- Concise planning
- Targeted exploration
- Focused implementation
- Key tests only

### Large Tasks (30k+ tokens)
- Strategic planning
- Efficient exploration (use Task tool)
- Incremental implementation
- Progressive testing

## Efficiency Metrics

### Tool Call Efficiency
- Target: <5 tool calls for simple tasks
- Target: <15 tool calls for medium tasks
- Use Task tool for >15 call tasks

### Response Length
- Simple tasks: 200-500 tokens
- Medium tasks: 500-1500 tokens
- Complex tasks: 1500-3000 tokens

### File Reading
- Read only what's needed
- Use offset/limit for large files
- Parallel reads when possible

## Trade-offs

### What to Preserve
✅ Correctness
✅ Type safety
✅ Test coverage
✅ Error handling
✅ Core functionality

### What to Minimize
❌ Explanatory text
❌ Repetitive context
❌ Verbose examples
❌ Obvious details
❌ Unnecessary tool calls

## Activation

This mode is automatically activated when:
- Large codebase (>100 files)
- Simple, focused tasks
- User requests efficiency
- Context approaching limits
- Rapid iteration needed

## Integration with Other Modes

- **Token Efficiency + Orchestration**: Parallel + minimal
- **Token Efficiency + Task Management**: Concise task descriptions
- **Token Efficiency + Implementation**: Minimal but complete

## Example Comparison

### Standard Response (2000 tokens)
```
I'll help you add severity filtering to the events API. This is an
important feature that will allow users to filter monitoring events
based on their importance level...

[Full architectural context]
[Detailed explanation of each step]
[Multiple code examples with comments]
[Comprehensive test examples]
[Detailed verification steps]
```

### Token Efficient Response (500 tokens)
```
Adding severity filter:

Domain (event.py:15):
  severity: int = Field(ge=0, le=4)

API (events/main.py:42):
  severity: int | None = Query(None, ge=0, le=4)
  events = use_case.execute(severity=severity)

Repository (event.py:87):
  if severity is not None:
      conditions.append(EventModel.severity == severity)

Test:
  assert len(get_events(severity=3)) == 5

✅ Done. All tests pass, coverage maintained at 91%.
```

**Savings: 75% fewer tokens, same outcome**
