# Contributing

Thanks for your interest in contributing to image-drift-generator! This document outlines our development workflow and expectations.

## Getting Started

1. Fork the repository and clone your fork locally:
   ```bash
   git clone https://github.com/your-username/image-drift-generator.git
   cd image-drift-generator
   ```

2. Set up your development environment:
   ```bash
   make setup
   make install
   ```

3. Install pre-commit hooks (optional but recommended):
   ```bash
   make pre-commit-install
   ```

## Development Workflow

### Before Making Changes

- Open an issue to discuss your proposed changes (especially for new features)
- Keep changes small and focused on a single concern
- Reference issue numbers in commit messages and pull requests

### Code Style and Quality

We follow PEP 8 and use automated tools for code formatting and linting:

- **Formatting**: Black and isort are used for code formatting
  ```bash
  make format  # Auto-format your code
  ```

- **Linting**: We use flake8 for code quality checks
  ```bash
  make lint    # Run flake8
  ```

- **Type Checking**: We use mypy for static type analysis
  ```bash
  make type-check
  ```

- **Pre-commit Hooks**: Configure hooks to catch issues before committing
  ```bash
  make pre-commit-install
  make pre-commit-run  # Run checks manually
  ```

### Testing

All code changes must include tests. We use pytest for testing:

```bash
make test              # Run all tests
pytest tests/test_generation.py -v    # Run specific test file
pytest tests/ -k TestConfigValidation  # Run specific test class
```

Test coverage is tracked. New code should maintain or improve coverage:

```bash
pytest --cov=src --cov-report=html tests/
```

### Type Hints

All functions should include type hints for parameters and return values:

```python
def load_and_scale_image() -> Image.Image:
    """Load and scale the input image.
    
    Returns:
        Pillow Image object in RGBA mode.
    """
    ...
```

### Documentation

- Include docstrings for all public functions using Google style
- Update README.md and USAGE.md for user-facing changes
- Add docstring comments for complex logic
- Update CONFIGURATION.md if you add new config options

Example docstring:

```python
def compute_base_position(img_w: int, img_h: int) -> Tuple[int, int]:
    """Compute the base position for pasting the image on the canvas.
    
    Args:
        img_w: Image width in pixels.
        img_h: Image height in pixels.
        
    Returns:
        Tuple of (x, y) coordinates.
        
    Raises:
        ConfigError: If position cannot be computed.
    """
```

## Submitting Changes

1. Create a descriptive commit message:
   ```
   Add type hints to generate_frames module
   
   - Add typing imports and type annotations to all functions
   - Improves IDE support and enables better static analysis
   - Fixes #42
   ```

2. Push your branch and open a pull request:
   - Reference relevant issues
   - Describe what your changes do and why
   - Include any testing you performed

3. Address review feedback:
   - Make requested changes in new commits
   - Re-run tests and linting
   - Respond to comments

## Code Organization

```
src/
  generate_frames.py  # Frame generation logic
  encode_webm.py      # WebM encoding logic
  logging_config.py   # Logging setup
  errors.py           # Custom exceptions
  __init__.py         # Package initialization

tests/
  test_generation.py  # Comprehensive test suite
  test_offsets.py     # Motion calculation tests

docs/
  USAGE.md            # User guide with examples
  CONFIGURATION.md    # Configuration reference
```

## Adding New Features

For new features:

1. Open an issue describing the feature
2. Discuss the design and implementation approach
3. Create a branch with a descriptive name: `feature/my-feature-name`
4. Implement with tests and documentation
5. Submit a pull request with clear description

Example: Adding a new motion mode

```python
def new_motion_offsets(t_seconds: float, duration: float) -> Tuple[float, float]:
    """Generate offsets using new motion algorithm.
    
    Args:
        t_seconds: Current time in seconds.
        duration: Total animation duration.
        
    Returns:
        Tuple of (dx, dy) offset values.
    """
    # Implementation
    return dx, dy
```

Then add tests:

```python
class TestNewMotion:
    """Test new motion mode."""
    
    def test_new_motion_offsets_returns_tuple(self):
        """Verify return type."""
        dx, dy = new_motion_offsets(0.5, 10.0)
        assert isinstance(dx, float)
        assert isinstance(dy, float)
```

## Docker Development

To test in Docker:

```bash
docker build -t image-drift-generator:dev .
docker run -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  image-drift-generator:dev
```

## Performance and Optimization

When optimizing performance:

1. Profile first to identify bottlenecks
2. Document performance improvements with metrics
3. Ensure changes don't reduce code clarity
4. Add performance test cases if appropriate

## Reporting Issues

When reporting bugs:

- Include Python version and OS
- Provide minimal reproduction steps
- Include error messages and logs
- Attach sample input if possible

## Questions?

- Check existing issues and discussions
- Look at code comments and docstrings
- Review USAGE.md and CONFIGURATION.md
- Open a discussion issue for architectural questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
