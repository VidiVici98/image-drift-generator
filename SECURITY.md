# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in image-drift-generator, please **do not** open a public issue. Instead:

1. Email the maintainers directly (check the GitHub profile)
2. Include a clear description of the vulnerability
3. Provide steps to reproduce if applicable
4. Give maintainers time to respond and prepare a fix before public disclosure

We take security seriously and will work to patch issues as soon as possible.

## Security Best Practices

### Input Validation

The project validates all configuration inputs on startup:

- Canvas dimensions must be positive
- Frame counts must be positive
- Motion modes must be valid ("perlin" or "sine")
- Base position modes must be valid ("center" or "coords")
- Image files must exist and be readable

### File Handling

- Input images are loaded via Pillow with format validation
- Output directories are created safely with proper permissions
- Temporary files are cleaned up automatically
- Large file uploads are limited in Docker builds

### Dependencies

We use only well-maintained, trustworthy dependencies:

- **Pillow**: Industry-standard image library
- **numpy**: Widely used numerical computing library
- **OpenSimplex**: Simple, focused noise generation
- **tqdm**: Popular progress bar library

Dependencies are pinned to specific versions in `requirements.txt` to ensure reproducibility.

### Docker Security

The Dockerfile follows security best practices:

- Uses slim base image to minimize attack surface
- Creates non-root user for container execution
- Doesn't install unnecessary tools
- Properly labels and documents build stages

Build with:
```bash
docker build -t image-drift-generator .
```

Run as non-root:
```bash
docker run --user appuser image-drift-generator
```

### Code Quality

- All functions include type hints for better static analysis
- Comprehensive test coverage ensures code reliability
- Linting catches potential issues before deployment
- Pre-commit hooks enforce standards

### Data Privacy

- The tool processes local files only
- No network communication occurs
- No telemetry or logging to external services
- Output files are stored locally

## Dependency Maintenance

Keep dependencies up to date:

```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

Review the GitHub security advisories tab for known vulnerabilities in dependencies.

## Responsible Disclosure Timeline

1. **Initial Report**: Submit vulnerability details
2. **Confirmation**: Maintainers acknowledge receipt within 48 hours
3. **Assessment**: Severity is determined within 1 week
4. **Development**: Patch is developed and tested
5. **Release**: Security fix is released and disclosed
6. **Announcement**: Vulnerability is published with credit to reporter

## Known Limitations

- The tool requires ffmpeg for WebM encoding; ffmpeg security is the responsibility of the ffmpeg project
- Input image formats are limited to those supported by Pillow
- Very large images or long animations may consume significant memory

## Additional Resources

- [OWASP Python Security Guide](https://owasp.org/www-community/controls/Python_Security)
- [Pillow Security Documentation](https://python-pillow.org/docs/)
- [Python Typing Documentation](https://docs.python.org/3/library/typing.html)
