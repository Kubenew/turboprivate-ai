# Contributing to TurboPrivate AI

Thank you for your interest in contributing! TurboPrivate AI is an open-source platform for self-hosted LLM inference with enterprise safety governance.

## Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Use the bug report template
3. Include:
   - OS, Python version, GPU info
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs (`turbo doctor` output)

### Suggesting Features

1. Check existing issues/roadmap
2. Use the feature request template
3. Describe the use case and priority

### Pull Requests

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** with tests
4. **Run checks**:
   ```bash
   ruff check .
   ruff format .
   pytest tests/
   ```
5. **Commit** with conventional commits:
   - `feat: add new feature`
   - `fix: resolve bug`
   - `docs: update documentation`
   - `test: add test coverage`
6. **Push** and open PR

## Development Setup

```bash
# Clone
git clone https://github.com/Kubenew/turboprivate-ai.git
cd turboprivate-ai

# Install dev dependencies
pip install -e ".[all]"

# Run tests
pytest tests/

# Lint
ruff check .
ruff format .
```

## Project Structure

```
turbo/          # Core platform code
  api/          # FastAPI routes and middleware
  inference/    # Model serving backends
  safety/       # Mythos Safe verifiers
  memory/       # RAG and vector store
  infra/        # K8s provisioning and backup
worker/         # Celery workers
examples/       # Integration examples
docs/           # Documentation
tests/          # Test suite
```

## Testing

- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Run all**: `pytest tests/ -v`
- **Coverage**: `pytest --cov=turbo tests/`

## Documentation

- Update `docs/` for new features
- Update `README.md` for user-facing changes
- Use Markdown with proper headings
- Include code examples where helpful

## Release Process

1. Version bump in `pyproject.toml`
2. Update `README.md` changelog
3. Tag release: `git tag v0.1.x`
4. Push: `git push origin main --tags`
5. CI builds and publishes to PyPI

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.

## Questions?

- **GitHub Discussions**: https://github.com/Kubenew/turboprivate-ai/discussions
- **Email**: hello@turboprivate.ai

---

*Thank you for helping make TurboPrivate AI better!*
