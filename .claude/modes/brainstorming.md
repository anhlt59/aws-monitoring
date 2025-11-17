# Brainstorming Mode

Activate creative, exploratory thinking for idea generation and problem-solving.

## Mode Characteristics

- **Divergent thinking** - Generate multiple ideas without immediate judgment
- **Question-driven** - Ask probing questions to uncover insights
- **Open exploration** - Consider unconventional and creative approaches
- **Multi-perspective** - View problems from different angles
- **Possibility focus** - "What if" and "How might we" thinking

## When to Use

- Designing new features or capabilities
- Solving challenging problems
- Exploring alternative approaches
- Innovation sessions
- Overcoming blockers
- Architectural decisions with trade-offs

## Mode Behavior

### Encouraged
- Generate multiple solution options
- Explore edge cases and variations
- Question assumptions
- Consider analogies from other domains
- Think about long-term implications
- Propose bold or unconventional ideas

### Avoid
- Premature optimization
- Immediate dismissal of ideas
- Over-focusing on constraints early
- Analysis paralysis
- Single-solution thinking

## Brainstorming Techniques Applied

### SCAMPER
- **Substitute**: What can we replace?
- **Combine**: What can we merge?
- **Adapt**: What can we adjust?
- **Modify**: What can we change?
- **Put to other uses**: What else could this do?
- **Eliminate**: What can we remove?
- **Reverse**: What if we did the opposite?

### Six Thinking Hats
- **White**: Facts and information
- **Red**: Emotions and intuition
- **Black**: Cautions and risks
- **Yellow**: Benefits and optimism
- **Green**: Creativity and alternatives
- **Blue**: Process and meta-thinking

### First Principles
- Break down to fundamental truths
- Question every assumption
- Rebuild from basics
- Identify root constraints

## Example Application

### Problem: How to reduce Lambda cold start times?

**Brainstorming Session:**

1. **Divergent thinking**
   - Provisioned concurrency
   - Smaller deployment packages
   - Pre-warming strategies
   - Alternative runtimes
   - Edge computing
   - Container reuse

2. **Question-driven**
   - What causes cold starts?
   - Which functions are most affected?
   - What's the actual user impact?
   - Are cold starts the real problem?

3. **Explore variations**
   - Hybrid approach: warm for critical functions
   - Predictive warming based on usage patterns
   - Move initialization outside handler
   - Lazy loading of dependencies

4. **Multi-perspective**
   - User perspective: Does latency matter for this use case?
   - Cost perspective: What's the cost-performance trade-off?
   - Operational perspective: Complexity of solution?
   - Technical perspective: Implementation feasibility?

5. **Synthesize**
   - Combine: Provisioned concurrency for critical paths + lazy loading
   - Evaluate: Cost vs performance improvement
   - Decide: Phased approach starting with measurement

## Activation

This mode is automatically activated when:
- Using `/brainstorm` command
- User requests creative exploration
- Multiple solution options are needed
- Problem requires innovative thinking

## Integration with Other Modes

- **Brainstorming → Design**: Generate ideas, then structure them
- **Brainstorming → Research**: Explore ideas, then validate with research
- **Brainstorming → Analyze**: Generate options, then evaluate systematically
