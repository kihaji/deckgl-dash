# Installation

## Install from PyPI

```bash
pip install deckgl-dash
```

### Optional Dependencies

For H3 hexagonal indexing support:

```bash
pip install deckgl-dash[test]
```

### Verify Installation

```bash
python -c "import deckgl_dash; print(deckgl_dash.__version__)"
```

## Development Setup

For contributors working on deckgl-dash itself:

```bash
# 1. Clone the repository
git clone https://github.com/kihaji/deckgl-dash.git
cd deckgl-dash

# 2. Install JavaScript dependencies
npm install

# 3. Build the JavaScript bundle
npm run build

# 4. Install Python package in development mode
pip install -e .
```

### Using Poetry (recommended for development)

```bash
# Install all dependencies including dev
poetry install

# Install with docs dependencies
poetry install --with docs

# Build JavaScript
npm install && npm run build
```

## Requirements

- **Python** >= 3.10
- **Dash** >= 2.0.0
- A modern browser with WebGL support
