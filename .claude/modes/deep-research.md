# Deep Research Mode

Activate comprehensive investigation with systematic information gathering and analysis.

## Mode Characteristics

- **Thorough investigation** - Exhaustive exploration of topics
- **Multi-source validation** - Cross-reference multiple sources
- **Evidence-based** - Grounded in documentation and facts
- **Contextual application** - Apply findings to project context
- **Comprehensive synthesis** - Combine insights into actionable recommendations

## When to Use

- Learning new technologies or patterns
- Investigating AWS service capabilities
- Understanding best practices
- Comparing implementation approaches
- Solving unfamiliar problems
- Validating architectural decisions

## Mode Behavior

### Research Process

1. **Define Research Question**
   - What specifically needs investigation?
   - What decisions depend on this research?
   - What depth is required?

2. **Gather Information**
   - Official documentation (AWS, Python, frameworks)
   - Best practices and patterns
   - Community knowledge and examples
   - Existing codebase patterns

3. **Analyze Findings**
   - Validate against project requirements
   - Identify applicable patterns
   - Evaluate trade-offs
   - Note constraints and limitations

4. **Synthesize Results**
   - Summarize key findings
   - Provide specific recommendations
   - Include code examples
   - Document decision rationale

5. **Apply to Context**
   - Map to project architecture
   - Consider existing patterns
   - Evaluate integration effort
   - Plan implementation approach

### Information Sources

1. **AWS Documentation**
   - Service documentation
   - API references
   - Best practices guides
   - Architecture patterns
   - Pricing information

2. **Python Ecosystem**
   - Library documentation
   - PEP standards
   - Type hints and validation
   - Testing frameworks
   - Package management

3. **Frameworks & Tools**
   - Serverless Framework docs
   - Pydantic documentation
   - Pytest documentation
   - LocalStack capabilities

4. **Codebase Context**
   - Existing implementations
   - Established patterns
   - Configuration files
   - Test fixtures

## Research Categories

### Technology Research
- AWS service features and limitations
- Python library capabilities
- Framework configurations
- Tool integrations

### Pattern Research
- Architectural patterns
- Design patterns
- AWS-specific patterns
- Testing patterns

### Best Practice Research
- Well-Architected Framework
- Security best practices
- Performance optimization
- Cost optimization

### Solution Research
- Alternative approaches
- Implementation strategies
- Migration paths
- Integration methods

## Example Research Flow

### Question: "What's the best approach for DynamoDB pagination?"

**Step 1: Define Scope**
- Need to paginate through large result sets
- Maintain performance at scale
- Support cursor-based pagination
- Compatible with PynamoDB

**Step 2: Gather Information**
- AWS DynamoDB pagination documentation
- PynamoDB query and scan methods
- Existing repository patterns in codebase
- Performance characteristics

**Step 3: Analyze Options**
- Option 1: LastEvaluatedKey pagination
- Option 2: Query with limit and scan forward
- Option 3: GSI with sort key for efficient paging
- Trade-offs: Complexity vs performance

**Step 4: Synthesize**
- Recommended: LastEvaluatedKey for simplicity
- Use base64 encoding for cursor
- Implement in base repository
- Add pagination helper utilities

**Step 5: Apply**
- Update base repository with pagination support
- Add cursor encoding/decoding utilities
- Create tests with large datasets
- Document pagination pattern

## Activation

This mode is automatically activated when:
- Using `/research` command
- User asks "how to" questions
- Investigating new technologies
- Comparing multiple options
- Need for comprehensive understanding

## Integration with Other Modes

- **Research → Design**: Validate design with research
- **Research → Implement**: Apply researched patterns
- **Research → Brainstorm**: Use findings to generate ideas
- **Sequential Thinking**: Structure complex research systematically

## Output Format

Research findings include:
- **Summary**: Key takeaways (3-5 bullets)
- **Detailed Findings**: Comprehensive analysis
- **Recommendations**: Specific, actionable suggestions
- **Code Examples**: Working code snippets
- **Trade-offs**: Pros and cons of each option
- **Next Steps**: Implementation guidance
