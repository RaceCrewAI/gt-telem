## Description
<!-- Describe your changes in detail -->

## Type of Change
<!-- Mark the relevant option with an "x" -->
- [ ] `feat`: New feature (minor version bump)
- [ ] `fix`: Bug fix (patch version bump)
- [ ] `docs`: Documentation changes
- [ ] `style`: Code style changes (formatting, etc.)
- [ ] `refactor`: Code refactoring
- [ ] `perf`: Performance improvements (patch version bump)
- [ ] `test`: Adding or updating tests
- [ ] `build`: Build system changes
- [ ] `ci`: CI/CD changes
- [ ] `chore`: Other changes that don't modify src or test files

## Breaking Changes
<!-- If this is a breaking change, describe the impact and migration path -->
- [ ] This PR contains breaking changes (major version bump)

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Commit Message Format
Please ensure your commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Example:
```
feat(telemetry): add support for new telemetry fields

Added support for tire wear and brake temperature fields
in the telemetry packet.

Closes #123
```
