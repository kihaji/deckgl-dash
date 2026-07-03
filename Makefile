# Makefile for deckgl-dash
#
# Usage:
#   make          - Build minified production version
#   make dev      - Build non-minified development version
#   make clean    - Remove build artifacts
#   make release VERSION=x.y.z - Verify clean tree + version consistency and tag for release
#   make check-versions [VERSION=x.y.z] - Verify all version sources agree (and match VERSION if given)
#   make docs-serve  - Serve docs locally at http://127.0.0.1:8000
#   make docs-build  - Build docs with strict mode
#

.PHONY: all build dev clean release check-git check-version check-versions quality docs-serve docs-build

# Default target - build production version
all: build

# Build minified production version
build:
	@echo "Building production (minified) version..."
	npm run build:js
	@echo "Build complete: deckgl_dash/deckgl_dash.min.js"

# Build development (non-minified) version
dev:
	@echo "Building development (non-minified) version..."
	npm run build:js -- --mode development
	@echo "Build complete: deckgl_dash/deckgl_dash.dev.js"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f deckgl_dash/deckgl_dash.min.js
	rm -f deckgl_dash/deckgl_dash.min.js.map
	rm -f deckgl_dash/deckgl_dash.min.js.LICENSE.txt
	rm -f deckgl_dash/deckgl_dash.dev.js
	rm -f deckgl_dash/deckgl_dash.dev.js.map
	@echo "Clean complete"

# Run code quality checks: ruff (lint) + Pyright (types)
quality:
	@echo "Running ruff linter..."
	uv run ruff check .
	@echo "Running Pyright type checker..."
	uv run npx pyright
	@echo ""
	@echo "Quality check complete."

# Check if git working directory is clean
check-git:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Working directory has uncommitted changes:"; \
		git status --short; \
		echo ""; \
		echo "Please commit or stash changes before releasing."; \
		exit 1; \
	fi
	@echo "Git working directory is clean"

# Check that VERSION is provided
check-version:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		echo "Usage: make release VERSION=x.y.z"; \
		exit 1; \
	fi
	@echo "Release version: $(VERSION)"

# Check that all version sources agree (and match VERSION when provided)
check-versions:
	uv run python scripts/check_versions.py $(VERSION)

# Release target - verify clean tree + version consistency and tag
# Run "make build" and commit before releasing (or use scripts/release.py to bump + build + commit)
release: check-version check-git check-versions
	@echo ""
	@echo "Creating git tag v$(VERSION)..."
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	@echo ""
	@echo "=========================================="
	@echo "Release v$(VERSION) prepared successfully!"
	@echo "=========================================="
	@echo ""
	@echo "To publish, run:"
	@echo "  git push && git push --tags"
	@echo ""

# Serve documentation locally
docs-serve:
	uv run mkdocs serve

# Build documentation with strict mode (catches broken links/warnings)
docs-build:
	uv run mkdocs build --strict
