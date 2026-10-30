# Reflection

*(The handout PDF did not list the four reflection questions, so these are the standard ones for this lab. Edit them if your instructor's wording differs.)*

**1. Which tool was most useful and why?**
Pylint, because it covered the most ground: the mutable default, bare except, unclosed files, globals and dead code. Bandit found only one issue, but it was the most serious (`eval`). Flake8 was quick to fix but low impact.

**2. Did any tool give a false positive, or miss something?**
Nothing was clearly false. They missed logic bugs, though: negative readings produced a negative bill (-192.50) and an unknown meter raised `KeyError`. I only found these by running the program and reading the output.

**3. How do the tools complement each other?**
Pylint checks quality and logic, Flake8 checks style, and Bandit checks security. The `eval` line appeared in both Pylint (W0123) and Bandit (B307). Each tool misses things the others catch.

**4. How would you use static analysis in a real project?**
Run all three in CI and as a pre-commit hook, and fail the build on Bandit findings and on a Pylint score below a threshold. Static analysis does not replace tests, because it cannot check business rules.
