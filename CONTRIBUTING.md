# Contributing to gt-telem

Thank you for your interest in contributing to gt-telem!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/RaceCrewAI/gt-telem.git
cd gt-telem
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated semantic versioning and changelog generation.

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature (triggers minor version bump)
- `fix`: Bug fix (triggers patch version bump)
- `perf`: Performance improvement (triggers patch version bump)
- `docs`: Documentation changes
- `style`: Code style/formatting changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes

### Breaking Changes
Add `BREAKING CHANGE:` in the footer or `!` after the type to trigger a major version bump:
```
feat!: remove deprecated API endpoint

BREAKING CHANGE: The /v1/old endpoint has been removed. Use /v2/new instead.
```

### Examples
```
feat(telemetry): add tire wear data support
fix(client): resolve connection timeout issue
docs: update installation instructions
ci: add automated PyPI deployment
```

## Pull Request Process

1. Create a feature branch from `main`:
```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

2. Make your changes and commit using conventional commits
3. Run tests and linting:
```bash
pytest tests/
pre-commit run --all-files
```

4. Push your branch and create a pull request
5. Ensure all CI checks pass
6. Wait for review and address any feedback

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=gt_telem --cov-report=term
```

## Code Style

This project uses:
- **black** for code formatting
- **isort** for import sorting
- **pre-commit** hooks for automated checks

Run formatting:
```bash
black gt_telem/ tests/
isort gt_telem/ tests/
```

## Release Process

Releases are automated via GitHub Actions when commits are pushed to the `main` branch:

1. Commits are analyzed for conventional commit messages
2. Version is bumped automatically based on commit types
3. Changelog is generated
4. Git tag is created
5. Package is built and published to PyPI

You don't need to manually bump versions or create releases!

## Questions?

Feel free to open an issue for any questions or concerns.
