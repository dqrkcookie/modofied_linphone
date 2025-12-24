# Contributing to Linphone SIP Audio Injector

First off, thank you for considering contributing to Linphone SIP Audio Injector! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our commitment to fostering an open and welcoming environment. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Call endpoint '...'
2. With payload '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
 - OS: [e.g., Ubuntu 20.04]
 - Python version: [e.g., 3.8.10]
 - Linphone version: [e.g., 4.2.5]

**Logs**
Please attach relevant logs from `logs/` directory.

**Additional context**
Any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** and description
- **Use case** - Why would this be useful?
- **Examples** - How would it work?
- **Alternatives** - What alternatives have you considered?

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Run the test suite**:
   ```bash
   pytest tests/ -v
   ```
6. **Format your code**:
   ```bash
   black app/
   isort app/
   ```
7. **Commit** with clear messages:
   ```bash
   git commit -m "Add feature: description of feature"
   ```
8. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Open a Pull Request** with a clear title and description

## Development Setup

### Prerequisites

```bash
# Install system dependencies
sudo apt update
sudo apt install -y linphone-cli python3.8 python3-pip

# Clone your fork
git clone https://github.com/rathnavel/linphone-sip-audio-injector.git
cd linphone-sip-audio-injector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_linphone_controller.py -v

# Run specific test
pytest tests/test_linphone_controller.py::test_start_call -v
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/

# Type check
mypy app/
```

### Pre-commit Hooks

We recommend setting up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Coding Standards

### Python Style Guide

- Follow PEP 8
- Use type hints for function signatures
- Write docstrings for all public functions/classes
- Keep functions small and focused
- Prefer async/await for I/O operations

### Example Function

```python
async def inject_audio(self, audio_file_name: str, silence_after_seconds: float = 1.5) -> None:
    """
    Inject audio into the active call.
    
    Args:
        audio_file_name: Name of the WAV file in assets/audio/
        silence_after_seconds: Duration of silence gap for RTP segmentation
        
    Raises:
        ValueError: If no call is active
        FileNotFoundError: If audio file not found
        
    Example:
        >>> await controller.inject_audio("greeting.wav", silence_after_seconds=2.0)
    """
    # Implementation
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add WebSocket support for real-time events

fix: resolve audio interruption race condition

docs: update API reference for playAudio endpoint

test: add integration tests for call lifecycle
```

## Project Structure

```
linphone-caller/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── call_logger.py     # Per-call logging
│   │   └── linphone_controller.py  # Main controller
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   └── main.py                # FastAPI app
├── assets/
│   └── audio/                 # Audio files
├── config/
│   └── linphonerc             # Linphone config
├── tests/
│   ├── test_api.py
│   ├── test_controller.py
│   └── conftest.py
├── scripts/
│   └── deploy.sh              # Deployment script
└── systemd/
    └── linphone-caller.service
```

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Mock external dependencies (linphonec process)
- Use pytest fixtures for common setup

### Integration Tests

- Test complete workflows (start call → inject audio → end call)
- Use real linphonec process if possible
- Clean up resources after tests

### Test Example

```python
import pytest
from app.core.linphone_controller import LinphoneController

@pytest.mark.asyncio
async def test_inject_audio_success():
    """Test successful audio injection."""
    controller = LinphoneController()
    
    # Setup: Start a call
    await controller.start_call("sip:test@example.com", duration_limit=60)
    
    # Act: Inject audio
    await controller.inject_audio("test_audio.wav")
    
    # Assert: Check call status
    call = controller.get_current_call()
    assert call is not None
    assert call.status == CallStatus.PLAYING_AUDIO
    
    # Cleanup
    await controller.end_call()
```

## Documentation

### Update Documentation

When adding features, update:
- **README.md** - User-facing documentation
- **API reference** - Endpoint documentation
- **PRODUCTION_READY.md** - Deployment guide
- **Code docstrings** - Developer documentation

### Documentation Style

- Use clear, concise language
- Provide examples for complex features
- Include error cases and troubleshooting
- Keep code examples up to date

## Release Process

1. Update version in `app/__init__.py`
2. Update `CHANGELOG.md`
3. Create release branch: `git checkout -b release/v1.1.0`
4. Test thoroughly
5. Merge to `main`
6. Tag release: `git tag v1.1.0`
7. Push: `git push origin v1.1.0`
8. Create GitHub release with changelog

## Questions?

Feel free to:
- Open a [GitHub Discussion](https://github.com/rathnavel/linphone-sip-audio-injector/discussions)
- Ask in [GitHub Issues](https://github.com/rathnavel/linphone-sip-audio-injector/issues)
- Contact via GitHub profile

Thank you for contributing! 🙏

