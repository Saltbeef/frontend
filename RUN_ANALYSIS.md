# Run Analysis CLI Tool

Modern CLI tool for analyzing houses locally using the same logic as the GitHub Action workflow.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `typer` - Modern CLI framework
- `rich` - Beautiful terminal output

### 2. Set Up API Keys

Create a `.env` file or set environment variables:

```bash
# Required for real analysis (optional for mock)
export ANTHROPIC_API_KEY="your-claude-api-key"

# Optional - for AirROI enrichment
export AIRROI_API_KEY="your-airroi-api-key"
```

### 3. Run Analysis

```bash
# Basic analysis with Claude
python run_analysis.py 43084820

# With specific rules version
python run_analysis.py 43084820 --rules v2.0.0

# Mock mode (no API costs, fast testing)
python run_analysis.py 43084820 --mock

# Skip enrichment (faster, no AirROI API call)
python run_analysis.py 43084820 --skip-enrichment

# Don't commit to git (for testing)
python run_analysis.py 43084820 --no-commit
```

## Usage

```bash
python run_analysis.py HOUSE_ID [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--rules VERSION` | `-r` | Rules version to use | `latest` |
| `--llm PROVIDER` | `-l` | LLM provider (mock/claude/openai) | `claude` |
| `--mock` | `-m` | Use mock LLM (no API costs) | `False` |
| `--skip-enrichment` | | Skip AirROI enrichment | `False` |
| `--force-enrichment` | | Force re-fetch enrichment data | `False` |
| `--no-commit` | | Skip git commit and push | `False` |
| `--no-reports` | | Skip report generation | `False` |

### Examples

```bash
# Quick test with mock LLM, no commit
python run_analysis.py 43084820 --mock --no-commit

# Full analysis with Claude and enrichment
python run_analysis.py 43084820 --rules v2.0.0 --llm claude

# Re-analyze with fresh enrichment data
python run_analysis.py 43084820 --force-enrichment

# Fast iteration: mock LLM, skip enrichment, no commit
python run_analysis.py 43084820 -m --skip-enrichment --no-commit
```

## What It Does

The script performs the same steps as the GitHub Action workflow:

1. **Load house data** from compressed dataset (`data/apify_dataset.json.gz`)
2. **Fetch enrichment data** from AirROI API (optional)
   - Comparable listings nearby
   - Revenue estimates
   - Geocoding if needed
3. **Load market metrics** for the city (if available)
4. **Run analysis** using the configured LLM provider
5. **Save results**:
   - Analysis JSON in `houses/{ID}/analyses/`
   - Raw data in `houses/{ID}/raw/`
   - Latest reference in `houses/{ID}/latest_analysis.json`
6. **Generate reports**:
   - HTML report with styling
   - Markdown report for easy viewing
   - Symlinks to latest reports
7. **Update scores index** in `data/analysis_scores.json`
8. **Commit and push** to git (optional)

## Output Structure

```
houses/43084820/
├── analyses/
│   └── v2.0.0_2025-11-13T20-30-45.json
├── enrichment/
│   └── airroi_enrichment.json
├── raw/
│   └── data_2025-11-13T20-30-45.json
├── reports/
│   ├── v2.0.0_2025-11-13T20-30-45.html
│   ├── v2.0.0_2025-11-13T20-30-45.md
│   ├── latest.html -> v2.0.0_2025-11-13T20-30-45.html
│   └── latest.md -> v2.0.0_2025-11-13T20-30-45.md
└── latest_analysis.json
```

## Benefits Over GitHub Action

1. **Faster iteration** - Run analyses locally without waiting for CI/CD
2. **Better feedback** - Rich terminal output with colors and progress
3. **Easy debugging** - Run with `--mock` and `--no-commit` for quick tests
4. **Cost control** - Use `--skip-enrichment` to avoid API costs
5. **Flexible** - Mix and match options for different use cases

## Troubleshooting

### Missing dependencies

```bash
pip install typer rich
```

### House not found

Make sure the dataset is up to date:
```bash
# Check when dataset was last updated
ls -lh data/apify_dataset.json.gz

# If needed, sync dataset (if you have the workflow set up)
gh workflow run sync_apify_dataset.yml
```

### API errors

- Check that your API keys are set correctly
- Use `--mock` to test without API calls
- Use `--skip-enrichment` to skip AirROI API calls

### Git push fails

- Make sure you're on the main branch
- Pull latest changes first: `git pull origin main`
- Use `--no-commit` to skip git operations during testing

## Integration with GitHub Actions

The GitHub Action workflow can be updated to use this script instead of inline Python code, making it easier to maintain and test locally.

See `.github/workflows/analyze_house.yml` for the workflow configuration.
