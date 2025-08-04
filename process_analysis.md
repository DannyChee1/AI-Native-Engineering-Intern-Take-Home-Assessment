# AI Native Development Process Analysis

## Loom Video

🎥 **[Watch the Loom Video](https://www.loom.com/share/410072be7ada4e99bb284d77be533991)**

---

### What worked well in my development process?

1. **Role-Based Prompting Strategy**
   - Using specific roles (e.g., "senior Python engineer") which provided higher-quality context-aware responses
   - AI understood the depth and requirements for each task
   - Generated proper error handling code

2. **Iterative Development Approach**
   - Started with broad refactoring prompts, then refined specific components based on the requirements
   - AI automatically identified and fixed issues during testing iteratively through feedback loops from itself and me

3. **Comprehensive Testingn**
   - AI generated a total of 37 unit tests covering a large set of edge cases, database operations and authentication logic
   - Successfully created automated unit tests using unittest and ensured to output what was working and what was not

4. **Documentation**
   - Detailed documentation throughout the process (in-line code, README.md)

### Problems I faced.

1. **Too Complex**
   - AI sometimes suggested features not yet needed (e.g. password hashing when I haven't told it yet)
   - So sometimes requires manual intervention to keep focus on priorities

2. **Package Import Issues**
   - There were a lot of `ModuleNotFoundError` for Flask and JWT despite proper installation, perhaps due to a non-functional virtual environment (environment issues)
   - Resulted in test cases being skipped and manual testing

## Recommendations for using Cursor in Team Settings

### 1. Prompt Template Library

**Create standardized prompt templates for common tasks:**

```markdown
## Code Refactoring Template
**Role:** [Specific role with expertise level]
**Context:** [Current state or provide file as context or specific output]
**Requirements:** [Clear limitations and requirements]
**Expected Output:** [Specific output needed]
```

### 2. General Modernization Strategy

**Setup** Perform necessary setup, general security rules and other requirements
**Analysis/Refactoring** AI reviews code and gives architecture refactoring suggestions and team discusses ideas
**Testing** AI generates test suites to cover comprehensive cases including ones we do not think of and we manually integrate the tests
**Documentation** As part of analysis, AI can generate documentation in the form of in-line docs or a markdown file and lay down standards for future developers.

## My thoughts

Using Cursor or AI during development process can impact the workflow significantly through analysis, documentation, and testing while maintaining high-quality when proper rules are lay out. It provides a standardized documentation process and also developes iteratively to ensure a feature is integrated smoothly.

### Reflection

This assessment relates to my other projects because in my other projects like the Rogo.ai replica with a Go Websocket System for Chatbot integration, I had to use Cursor to explain stuff and steps on how to deploy the infrastructure. Through this assessment, I learned how to prompt more effectively, how to write unit tests for each component which I haven't done previously, and to write clear and detailed documentation (that I didn't for other projects).

The difference this time was how I approached AI-enhanced development. Instead of just asking for explanations, I learned to structure prompts with specific roles, clear constraints, and expected outputs. This made the AI responses much more targeted and useful. The iterative testing approach was also new to me as having AI generate comprehensive unit tests and reiterating to further refine the product created a more robust final output.

## Large-Scale Architecture Revamp Suggestion

For a large-scale architecture revamp, I would recommend implementing an AI-powered code audit and a pipeline from migrating monolithic code to a more revamped codebase. How it would work:

- Use AI to analyze the entire codebase to identify any architectural issues, dependencies issues, code smells, technical debt etc..
- Generate a migration roadmap (plans + deadlines) with requirements, changes to current infrastructure, and other recommendations/potential issues
- As well, break down each component into modularized code so that the migration happens in small chunks that we can manage safely and carefully
- Implement unit tests/integration tests for each component at each step of the way
- Use Cursor to generate proper documentation based on the previous analysis so it is consistent and easy to understand (+ saves a lot of time).

These steps would allow teams to tackle large-scale projects that need refactoring, using AI to their full advantage by identifying any underlying issues/risks, easily generate comprehensive tests, and maintain detailed documentation throughout the process. 
