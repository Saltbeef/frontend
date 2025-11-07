# House Analysis Agent Service

AI-powered analysis service for evaluating short-stay rental properties. This service uses LLM agents to analyze properties based on versioned rules, storing complete analysis history in Git for full auditability.

## 🎯 Overview

This service provides:

- **Versioned Analysis Rules**: Semantic versioning (v1.0.0, v2.0.0) for rule evolution
- **Complete Audit Trail**: All analyses stored in Git with timestamps
- **GitHub Actions Integration**: Async processing triggered via API
- **Apify Integration**: Fetch house data and update analysis status
- **HTML Reports**: Beautiful, printable analysis reports
- **Re-analysis Support**: Analyze houses again with new rule versions

## 🏗️ Architecture

```
[HTML SPA]
    ↓ GitHub API (workflow_dispatch)
[GitHub Actions]
    ↓ Apify API
[Fetch House Data]
    ↓ LLM Analysis (Claude/OpenAI)
[Generate Analysis]
    ↓ Git Commit
[houses/{id}/analyses/v1.0.0_{timestamp}.json]
    ↓ Update Summary
[Apify Key-Value Store]
    ↓ SPA Polls
[Display Results]
```

## 📁 Directory Structure

```
house-analysis/
├── .github/
│   └── workflows/
│       ├── analyze_house.yml       # Single house analysis
│       └── bulk_reanalyze.yml      # Bulk re-analysis
├── src/
│   ├── agent.py                    # LLM orchestrator
│   ├── apify_client.py            # Apify integration
│   └── report_generator.py        # HTML report generation
├── rules/
│   ├── base.py                     # Base rules class
│   ├── v1_0_0.py                  # Version 1.0.0 rules
│   └── registry.py                 # Version management
├── templates/
│   ├── analysis_schema.json       # JSON schema
│   └── report.html                 # HTML template
├── houses/                         # Git-tracked analyses
│   └── {house-id}/
│       ├── metadata.json
│       ├── raw/                    # Raw Apify data
│       ├── analyses/               # Analysis results
│       └── reports/                # HTML reports
├── analyze.py                      # CLI tool for local testing
└── README.md
```

## 🚀 Setup

### 1. GitHub Secrets

Add these secrets to your repository (Settings → Secrets and variables → Actions):

- `APIFY_API_TOKEN`: Your Apify API token
- `ANTHROPIC_API_KEY`: Your Anthropic Claude API key (if using Claude)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)

### 2. Enable GitHub Actions

Ensure GitHub Actions is enabled in your repository settings.

### 3. Local Development (Optional)

```bash
cd house-analysis
python3 analyze.py --house-id test123 --dataset-id YOUR_DATASET --mock
```

No dependencies needed - uses Python standard library only.

## 📝 Usage

### Trigger from HTML SPA

```javascript
// Trigger analysis via GitHub API
async function analyzeHouse(houseId) {
  const response = await fetch(
    'https://api.github.com/repos/OWNER/REPO/actions/workflows/analyze_house.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Authorization': 'token YOUR_PERSONAL_ACCESS_TOKEN',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: {
          house_id: houseId,
          apify_dataset_id: 'YOUR_DATASET_ID',
          rules_version: 'latest',
          llm_provider: 'claude'
        }
      })
    }
  );

  if (response.ok) {
    console.log('Analysis triggered for house:', houseId);
    // Poll Apify for status updates
    pollAnalysisStatus(houseId);
  }
}

// Poll for analysis completion
async function pollAnalysisStatus(houseId) {
  const apifyUrl = `https://api.apify.com/v2/key-value-stores/default/records/analysis_${houseId}?token=YOUR_TOKEN`;

  const interval = setInterval(async () => {
    const response = await fetch(apifyUrl);

    if (response.ok) {
      const status = await response.json();

      if (status.status === 'completed') {
        clearInterval(interval);
        console.log('Analysis complete! Score:', status.score);
        // Update UI with results
      } else if (status.status === 'failed') {
        clearInterval(interval);
        console.error('Analysis failed');
      }
    }
  }, 5000); // Poll every 5 seconds
}
```

### Manual Trigger (GitHub UI)

1. Go to **Actions** tab
2. Select **Analyze House** workflow
3. Click **Run workflow**
4. Enter parameters:
   - House ID
   - Apify Dataset ID
   - Rules version (default: latest)
   - LLM provider (default: claude)

### Local Testing

```bash
# Test with mock LLM (no API cost)
python analyze.py --house-id abc123 --dataset-id xyz --mock

# Test with real Claude API
export ANTHROPIC_API_KEY=sk-ant-...
python analyze.py --house-id abc123 --dataset-id xyz --llm claude

# Use specific rules version
python analyze.py --house-id abc123 --dataset-id xyz --rules v1.0.0 --mock
```

## 📊 Analysis Output

Each analysis produces:

### 1. JSON Analysis File
`houses/{id}/analyses/v1.0.0_2025-01-07T14-30-22.json`

```json
{
  "house_id": "abc123",
  "analyzed_at": "2025-01-07T14:30:22Z",
  "rules_version": "v1.0.0",
  "overall_score": 8.5,
  "category_scores": {
    "location": {
      "score": 9.0,
      "reasoning": "Excellent central location...",
      "red_flags": [],
      "recommendations": ["Verify parking"]
    },
    "property": { ... },
    "financial": { ... },
    "legal": { ... }
  },
  "overall_assessment": "Strong investment potential...",
  "top_strengths": [...],
  "top_concerns": [...],
  "investment_recommendation": "BUY|CONSIDER|PASS"
}
```

### 2. HTML Report
`houses/{id}/reports/v1.0.0_2025-01-07T14-30-22.html`

Beautiful, printable HTML report with:
- Overall score visualization
- Category breakdowns with scores
- Red flags and recommendations
- Investment recommendation

### 3. Raw Data Archive
`houses/{id}/raw/data_2025-01-07T14-30-22.json`

Original Apify data for reference.

### 4. Latest Analysis Reference
`houses/{id}/latest_analysis.json`

Quick reference to most recent analysis.

## 🔄 Versioned Rules System

### Current Version: v1.0.0

Categories (with weights):
- **Location** (25%): Proximity to attractions, transport, safety
- **Property** (30%): Size, condition, amenities, presentation
- **Financial** (30%): Pricing, revenue potential, ROI
- **Legal** (15%): Regulations, permits, compliance

### Adding New Rules Version

```python
# rules/v2_0_0.py
from .base import BaseRules, CategoryCriteria

class RulesV2_0_0(BaseRules):
    @property
    def version(self) -> str:
        return "v2.0.0"

    @property
    def categories(self) -> Dict[str, CategoryCriteria]:
        return {
            # New categories or updated weights
            "location": CategoryCriteria(...),
            "sustainability": CategoryCriteria(...),  # New!
            # ...
        }
```

Then register in `rules/registry.py`:

```python
from .v2_0_0 import RulesV2_0_0

class RulesRegistry:
    _rules: Dict[str, Type[BaseRules]] = {
        "v1.0.0": RulesV1_0_0,
        "v2.0.0": RulesV2_0_0,  # Add new version
    }
```

### Re-analyzing with New Rules

```bash
# Bulk re-analyze all houses with new rules
# Go to Actions → Bulk Re-analyze Houses
# Inputs:
#   - Apify Dataset ID: xyz
#   - Rules Version: v2.0.0
#   - House IDs: (leave empty for all, or comma-separated list)
```

## 🔌 Apify Integration

### Data Structure Expected

The service expects house data with these fields (adjust in code if different):

```json
{
  "id": "abc123",
  "title": "Beautiful City Center Apartment",
  "address": "123 Main St, Amsterdam",
  "price_per_night": 150,
  "bedrooms": 2,
  "bathrooms": 1,
  "square_meters": 75,
  "amenities": ["wifi", "kitchen", "parking"],
  "description": "...",
  "photos": ["url1", "url2"],
  "host_info": { ... },
  "reviews": [ ... ]
}
```

### Status Updates

The service updates Apify Key-Value Store with:

```json
{
  "house_id": "abc123",
  "status": "pending|processing|completed|failed",
  "score": 8.5,
  "updated_at": "2025-01-07T14:30:22Z",
  "analysis_url": "https://github.com/..."
}
```

Access via: `https://api.apify.com/v2/key-value-stores/default/records/analysis_{house_id}`

## 🎨 Customization

### Custom Analysis Criteria

Edit `rules/v1_0_0.py` to modify:
- Categories and weights
- Scoring criteria
- Prompt templates
- LLM instructions

### Custom HTML Reports

Edit `templates/report.html` to change:
- Styling and branding
- Report sections
- Data visualization

### Custom LLM Integration

Add new LLM provider in `src/agent.py`:

```python
class CustomLLM:
    def analyze(self, prompt: str) -> str:
        # Your LLM API call
        return json_response
```

## 🧪 Testing

### Test with Mock LLM

```bash
python analyze.py --house-id test --dataset-id xyz --mock
```

This generates realistic mock data without API costs.

### Validate Schema

```bash
python -c "
import json
from jsonschema import validate

with open('templates/analysis_schema.json') as f:
    schema = json.load(f)

with open('houses/abc123/analyses/v1.0.0_timestamp.json') as f:
    analysis = json.load(f)

validate(instance=analysis, schema=schema)
print('✅ Schema valid')
"
```

## ⚡ Performance

- **Analysis Time**: < 3 minutes per house (including LLM API)
- **Concurrent Analyses**: Up to 5 (configurable in bulk workflow)
- **No Database**: All data in Git (scales indefinitely)
- **No Dependencies**: Pure Python stdlib (fast CI/CD)

## 🔒 Security

- **API Keys**: Stored in GitHub Secrets (never in code)
- **Personal Access Token**: Required for workflow dispatch from SPA
  - Scope: `repo` or `workflow`
  - Store securely (later: move to Cloudflare Worker)
- **Apify Token**: Read/write access to datasets and key-value stores
- **LLM API Keys**: Protected in GitHub Secrets

## 🚧 Roadmap

- [ ] Cloudflare Worker for secure PAT management
- [ ] Webhook support for instant updates
- [ ] Multi-language support
- [ ] PDF report generation
- [ ] Comparative analysis (multiple houses)
- [ ] Historical trend analysis
- [ ] Rules A/B testing

## 📄 License

Part of the Saltbeef/frontend project.

## 🤝 Contributing

To add new features:

1. Keep all code in `house-analysis/` directory
2. Don't modify existing frontend files
3. Use semantic versioning for rules
4. Add tests for new LLM providers
5. Update this README

## 🆘 Troubleshooting

### Workflow fails with "House not found"

- Verify `apify_dataset_id` is correct
- Check `house_id` exists in dataset
- Ensure `APIFY_API_TOKEN` secret is set

### LLM API timeout

- Check API key is valid
- Verify API endpoint is accessible
- Try with `--mock` first to isolate issue

### Git commit fails

- Ensure GitHub Actions has write permission
- Check branch protection rules
- Verify workflow has correct permissions

### Apify status not updating

- Check `APIFY_API_TOKEN` is valid
- Verify Key-Value Store access
- Check API endpoint in `apify_client.py`

## 📞 Support

For issues or questions:
- Check GitHub Actions logs
- Review Apify dataset structure
- Test locally with `--mock` flag
- Open issue in repository
