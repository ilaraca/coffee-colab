# Conventions

Coding standards, naming conventions, and development practices followed in the project.

## Code Quality & Style
- **Linter**: **Ruff** is used for linting and code formatting.
- **Line Length**: Set to **88** characters (standard Black formatting).
- **Imports**: `isort`-like sorting is enforced via Ruff.

## Naming Conventions
- **Files**: Snake case (`snake_case.py`).
- **Classes**: Pascal case (`PascalCase`).
- **Functions/Variables**: Snake case (`snake_case`).
- **Models**: Pluralized directory (`models/`), singular file and class names (`user.py` -> `User`).
- **Routes**: Prefixed with `routes_` (`routes_auth.py`).

## Project Structure
- **Modularity**: Logic is split into `models`, `repos`, `services`, and `web` to maintain separation of concerns.
- **Templates**: Organized in `app/templates/`, using Jinja2 inheritance (e.g., `base.html`).

## Development Workflow
- **Guardrails**: Developers are encouraged to run `./verify.sh` before committing to ensure code quality and test coverage.
- **Environment**: Local development uses a `.env` file for secrets and configuration.

## UI & Design Principles
- **Aesthetics & Tone**: Maintain a highly professional, premium visual identity.
- **No Emojis**: Do **NOT** use emojis in the user interface (buttons, headers, copy, etc.) or documentation. Use professional SVG icons (like Lucide or Heroicons) instead, to ensure the platform conveys trust and a premium feel for both businesses and creatives.
