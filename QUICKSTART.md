# Quick Start Guide

Get started with the House Analysis Agent Service in 5 minutes.

## 🚀 Fastest Way to Test

```bash
# 1. Navigate to house-analysis directory
cd house-analysis

# 2. Run the complete flow test (no API keys needed!)
python test_complete_flow.py

# 3. Open the generated HTML report
# Look for output like: test_output/test_demo_001/reports/v1.0.0_*.html
```

This creates a complete analysis with mock data - **no API keys required!**

## 📋 Prerequisites

- Python 3.7+ (no additional packages needed)
- GitHub repository with Actions enabled
- Apify account with dataset containing house data

## ⚙️ Setup for Production

### Step 1: Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:

```
APIFY_API_TOKEN         # Your Apify API token
ANTHROPIC_API_KEY       # For Claude (or OPENAI_API_KEY for OpenAI)
```

### Step 2: Prepare Apify Dataset

Your Apify dataset should contain house records with fields like:

```json
{
  "id": "house_001",
  "title": "Beautiful Apartment",
  "address": "Street 123, City",
  "price_per_night": 150,
  "bedrooms": 2,
  "description": "...",
  ...
}
```

See `examples/apify-data-structure.json` for complete structure.

### Step 3: Test Locally

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Test with real API
export APIFY_API_TOKEN=your_token
export ANTHROPIC_API_KEY=your_key

python analyze.py \
  --house-id YOUR_HOUSE_ID \
  --dataset-id YOUR_DATASET_ID \
  --llm claude
```

### Step 4: Trigger from GitHub UI

1. Go to **Actions** tab in your repository
2. Select **Analyze House** workflow
3. Click **Run workflow**
4. Fill in:
   - House ID: `house_001`
   - Apify Dataset ID: `your_dataset_id`
   - Rules version: `latest`
   - LLM provider: `claude`
5. Click **Run workflow**

Results will be committed to: `houses/house_001/`

### Step 5: Integrate with Your SPA

```javascript
// Trigger analysis
async function analyzeHouse(houseId) {
  const response = await fetch(
    'https://api.github.com/repos/YOUR_ORG/YOUR_REPO/actions/workflows/analyze_house.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Authorization': `token ${YOUR_GITHUB_PAT}`,
        'Accept': 'application/vnd.github.v3+json'
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
    // Start polling for results
    pollForResults(houseId);
  }
}

// Poll for results
async function pollForResults(houseId) {
  const interval = setInterval(async () => {
    const status = await fetch(
      `https://api.apify.com/v2/key-value-stores/default/records/analysis_${houseId}?token=${YOUR_APIFY_TOKEN}`
    ).then(r => r.json());

    if (status.status === 'completed') {
      clearInterval(interval);
      console.log('Analysis complete!', status);
      // Update UI with score and link
      showResults(status);
    }
  }, 5000); // Poll every 5 seconds
}
```

See `examples/spa-integration.html` for complete working example.

## 🎯 Common Use Cases

### Analyze a Single House

```bash
python analyze.py --house-id abc123 --dataset-id xyz --llm claude
```

### Test Without API Costs

```bash
python analyze.py --house-id abc123 --dataset-id xyz --mock
```

### Bulk Re-analyze with New Rules

1. Update rules in `rules/v2_0_0.py`
2. Register in `rules/registry.py`
3. Go to Actions → **Bulk Re-analyze Houses**
4. Enter rules version: `v2.0.0`

### Local Development

```bash
# Run complete test suite
python test_complete_flow.py

# View generated report
open test_output/test_demo_001/reports/*.html

# Check generated files
ls -R test_output/test_demo_001/
```

## 📁 Understanding Output Structure

After analysis, you'll find:

```
houses/
  {house-id}/
    ├── latest_analysis.json          # Quick reference
    ├── raw/
    │   └── data_2025-01-07.json     # Original Apify data
    ├── analyses/
    │   └── v1.0.0_2025-01-07.json   # Full analysis
    └── reports/
        └── v1.0.0_2025-01-07.html   # Beautiful HTML report
```

## 🔧 Customization

### Change Analysis Criteria

Edit `rules/v1_0_0.py`:

```python
"location": CategoryCriteria(
    name="Location & Accessibility",
    weight=0.30,  # Change weight
    criteria=[
        "Add new criteria here",
        ...
    ]
)
```

### Modify HTML Report Style

Edit `templates/report.html` - change CSS, colors, layout.

### Add New LLM Provider

Edit `src/agent.py`:

```python
class MyCustomLLM:
    def analyze(self, prompt: str) -> str:
        # Your API call here
        return json_response
```

## 🐛 Troubleshooting

### "House not found in dataset"

- Check `house_id` matches exactly
- Verify `apify_dataset_id` is correct
- Test API access: `curl https://api.apify.com/v2/datasets/{id}/items?token={token}`

### Workflow fails with "Unauthorized"

- Check GitHub Actions has write permissions
- Verify secrets are added correctly
- Ensure PAT has `workflow` scope

### LLM API timeout

- Try with `--mock` first to isolate issue
- Check API key is valid
- Verify API quota/credits

### Analysis doesn't update in Apify

- Check Apify token has write access to Key-Value Store
- Verify Key-Value Store exists (default store is auto-created)
- Check logs in GitHub Actions workflow

## 📚 Next Steps

- [ ] Read full [README.md](README.md) for detailed docs
- [ ] Review [examples/](examples/) for integration patterns
- [ ] Customize rules for your specific needs
- [ ] Set up GitHub secrets for production
- [ ] Integrate with your frontend
- [ ] Monitor workflow runs and optimize

## 💡 Tips

1. **Start with mock LLM** - Test everything without API costs
2. **Use specific rules versions** - Avoid `latest` in production for reproducibility
3. **Monitor API costs** - Each analysis costs ~$0.10-0.50 depending on LLM
4. **Batch analyses** - Use bulk workflow during off-peak hours
5. **Cache results** - Don't re-analyze unless data changes significantly

## 🆘 Need Help?

- Check [README.md](README.md) for full documentation
- Review workflow logs in GitHub Actions
- Test locally with `--mock` flag
- See [examples/](examples/) for working code

## 🎉 You're Ready!

The service is fully functional. Start analyzing houses and get AI-powered investment insights in minutes!
