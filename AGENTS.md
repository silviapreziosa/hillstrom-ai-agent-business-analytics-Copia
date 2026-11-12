# AGENTS.md

This project evaluates the reliability of an AI agent performing Business Analytics. The agent must produce statistically sound, reproducible analyses and allow independent verification of its results.

## Professor's Rules

1. Never modify anything in data/raw/.
2. After every filter, merge or drop, print the number of rows and the reason.
3. Every number in a write-up comes from a file in results/; name the script that made it.
4. Follow plan.md. Ask before changing anything in it, and list every analysis choice you make.
5. Fix random seeds, and log the prompt, output and model name of every model call.
6. No causal claims unless the design supports them. Say "I am not sure" when you are not.

## Verification and Audit Rules

7. Before each analysis, explain the statistical method you propose, its assumptions, and why it fits the research question.
8. Never silently remove observations or variables. Document all data transformations.
9. For every main statistical result, save enough information to reproduce the calculation independently.
10. Explicitly report missing data, outliers, sample sizes, and relevant limitations.
11. Do not interpret correlation as causation without a valid causal identification strategy.
12. Record any detected analytical error, its cause, its correction, and the outcome of re-testing in mistakes.md.
13. Do not claim that a verification test passed unless the test was actually executed and its output was inspected.
14. Record the exact model identifier, analysis choices, and execution details needed for reproducibility.
