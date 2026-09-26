# Taskboard — Team Style Guide

1. **Naming**: `snake_case` for functions, methods and variables; `PascalCase` for classes.
2. **Type hints** on every public function and method signature.
3. **Docstrings** on every public function, method and class.
4. **No `print()`** in library code. Use the module-level `logger = logging.getLogger(__name__)`.
5. **No bare `except:`** and no silently swallowed exceptions. Catch specific exceptions and
   either handle them meaningfully or re-raise.
6. **Tests**: every new public function ships with tests in `tests/`, including edge cases
   (empty input, boundaries, missing ids).
7. Keep functions short and focused; prefer returning values over mutating arguments.
