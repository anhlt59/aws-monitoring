# Orchestration Mode

Activate efficient multi-tool coordination and parallel task execution.

## Mode Characteristics

- **Parallel execution** - Execute independent tasks simultaneously
- **Efficient planning** - Minimize sequential dependencies
- **Resource optimization** - Use appropriate tools for each task
- **Batch operations** - Group related operations
- **Smart delegation** - Use specialized agents when appropriate

## When to Use

- Complex tasks with multiple independent steps
- Large-scale codebase exploration
- Batch file operations
- Parallel test execution
- Multi-component deployments
- Comprehensive analysis requiring multiple tools

## Mode Behavior

### Orchestration Principles

1. **Identify Independent Tasks**
   - Which tasks have no dependencies?
   - What can run in parallel?
   - What requires sequential execution?

2. **Select Optimal Tools**
   - Use Glob for file discovery
   - Use Grep for content search
   - Use Read for file access
   - Use Task tool for complex analysis
   - Use Bash for command execution

3. **Batch Operations**
   - Group similar operations
   - Minimize context switching
   - Reduce total execution time
   - Optimize for performance

4. **Parallel Execution**
   - Run independent tool calls together
   - Maximize throughput
   - Reduce user wait time
   - Maintain clarity in results

### Tool Selection Strategy

| Task Type | Optimal Tool | Reason |
|-----------|--------------|--------|
| File pattern matching | Glob | Fast, designed for patterns |
| Content search | Grep | Efficient, powerful regex |
| File reading | Read | Direct, supports multiple files |
| Complex exploration | Task (Explore agent) | Thorough, iterative |
| Command execution | Bash | Direct system access |
| Multiple file edits | Edit (parallel) | Efficient, atomic |

## Example Orchestration

### Task: Analyze event handling across codebase

**Sequential Approach (Slow):**
```
1. Find event models
2. Find event handlers
3. Find event tests
4. Read model file
5. Read handler file
6. Read test file
```

**Orchestrated Approach (Fast):**
```
1. Parallel file discovery:
   - Glob("src/domain/models/**/event*.py")
   - Glob("src/entrypoints/**/*event*.py")
   - Glob("tests/**/*event*.py")

2. Parallel content search:
   - Grep("class.*Event", type="py")
   - Grep("def.*handle.*event", type="py")
   - Grep("test_.*event", type="py")

3. Parallel file reads:
   - Read(all discovered files in parallel)
```

### Task: Update multiple files

**Sequential Approach:**
```
1. Edit file1.py
2. Edit file2.py
3. Edit file3.py
```

**Orchestrated Approach:**
```
Parallel:
- Edit file1.py
- Edit file2.py
- Edit file3.py
```

### Task: Comprehensive test coverage analysis

**Orchestrated Approach:**
```
1. Parallel data gathering:
   - Bash("make test")
   - Glob("src/**/*.py")
   - Glob("tests/**/*.py")

2. Analyze results concurrently:
   - Parse coverage report
   - Map source files to test files
   - Identify gaps

3. Generate recommendations
```

## Orchestration Patterns

### Pattern 1: Parallel Discovery
```
Simultaneously:
- Find all Python files
- Find all test files
- Find all configuration files
- Search for specific patterns
```

### Pattern 2: Batch File Operations
```
Simultaneously:
- Read multiple related files
- Edit multiple files with same pattern
- Search across multiple directories
```

### Pattern 3: Multi-Stage Pipeline
```
Stage 1 (Parallel):
- Discover all components
- Search for patterns
- Gather metrics

Stage 2 (Sequential):
- Analyze gathered data
- Generate insights

Stage 3 (Parallel):
- Apply fixes
- Update documentation
- Run validations
```

### Pattern 4: Agent Delegation
```
Parallel agent invocation:
- Backend Architect: Analyze architecture
- Python Expert: Review code quality
- Test Expert: Assess test coverage

Synthesize: Combine all findings
```

## Optimization Techniques

### 1. Minimize Sequential Dependencies
```python
# ❌ Sequential
find_files()
then search_content()
then read_files()

# ✅ Parallel where possible
parallel:
  - find_files()
  - search_content()
then: read_files()  # Only after discovery
```

### 2. Batch Similar Operations
```python
# ❌ Individual
Read(file1)
Read(file2)
Read(file3)

# ✅ Batched (parallel)
parallel:
  - Read(file1)
  - Read(file2)
  - Read(file3)
```

### 3. Use Appropriate Tools
```python
# ❌ Wrong tool
Bash("find . -name '*.py'")  # Slower, less structured

# ✅ Right tool
Glob("**/*.py")  # Faster, better output format
```

## Activation

This mode is automatically activated when:
- Multiple independent tasks identified
- Large-scale operations needed
- Performance optimization required
- Complex multi-tool workflows

## Integration with Other Modes

- **Orchestration + Token Efficiency**: Minimize tool calls, maximize parallelism
- **Orchestration + Task Management**: Coordinate parallel todos
- **Orchestration + Deep Research**: Parallel information gathering

## Performance Metrics

Orchestration mode targets:
- 50-70% reduction in total execution time
- 3-5x more tool calls per message (parallel)
- Minimal sequential bottlenecks
- Optimal tool selection for each task
