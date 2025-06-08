.PHONY: install test test-unit test-integration lint format clean run dev-install

# Install production dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Install development dependencies
dev-install: install
	pip install -r requirements.txt

# Run all tests
test:
	pytest tests/ -v

# Run only unit tests (no API calls)
test-unit:
	pytest tests/ -v -m "not integration"

# Run integration tests (requires real credentials)
test-integration:
	pytest tests/ -v -m integration

# Run tests with coverage
test-coverage:
	pytest tests/ --cov=social_media_mcp --cov-report=html --cov-report=term

# Lint code
lint:
	ruff check src/
	mypy src/

# Format code
format:
	black src/ tests/
	ruff check --fix src/ tests/

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the server
run:
	python -m social_media_mcp

# Run development server with auto-reload
dev:
	python test_server.py

# Build documentation
docs:
	cd docs && make html

# Check if all tests pass before committing
pre-commit: format lint test-unit

# Create distribution packages
build: clean
	python -m build

# Upload to PyPI (requires credentials)
publish: build
	python -m twine upload dist/*