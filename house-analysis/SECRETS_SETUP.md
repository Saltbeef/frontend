# 🔐 Setting Up GitHub Secrets

This guide walks you through adding API secrets to your GitHub repository.

## Required Secrets

You need to add the following secrets:

- **APIFY_API_TOKEN** - Your Apify API token (starts with `apify_api_`)
- **ANTHROPIC_API_KEY** - Your Anthropic Claude API key (starts with `sk-ant-api03-`)

> **Note:** The actual token values were provided separately. Do not commit API tokens to the repository!

## Step-by-Step Instructions

### 1. Navigate to Your Repository

Open your browser and go to:
```
https://github.com/Saltbeef/frontend
```

### 2. Open Settings

- Click the **Settings** tab at the top of the repository page

### 3. Navigate to Secrets

- In the left sidebar, under **Security**, find **Secrets and variables**
- Click on **Actions**

### 4. Add First Secret - Apify Token

- Click the **"New repository secret"** button (green button on the right)
- Fill in:
  - **Name**: `APIFY_API_TOKEN`
  - **Secret**: [Paste your Apify token here - starts with `apify_api_`]
- Click **"Add secret"**

### 5. Add Second Secret - Anthropic API Key

- Click **"New repository secret"** again
- Fill in:
  - **Name**: `ANTHROPIC_API_KEY`
  - **Secret**: [Paste your Anthropic API key here - starts with `sk-ant-api03-`]
- Click **"Add secret"**

### 6. Verify Secrets Are Added

You should now see both secrets listed:
```
✅ APIFY_API_TOKEN          Updated now
✅ ANTHROPIC_API_KEY        Updated now
```

## 🧪 Verify Secrets Are Working

### Option 1: GitHub Actions (Recommended)

1. Go to the **Actions** tab in your repository
2. Select the **"Verify API Secrets"** workflow from the left sidebar
3. Click **"Run workflow"** button
4. Click the green **"Run workflow"** button in the dropdown
5. Wait for the workflow to complete (~30 seconds)
6. Check the results - you should see:
   ```
   ✅ APIFY_API_TOKEN is set
   ✅ ANTHROPIC_API_KEY is set
   ✅ Apify API verified!
   ✅ Anthropic API verified!
   ```

### Option 2: Local Verification

If you want to test locally first:

```bash
cd house-analysis

# Set environment variables (replace with your actual tokens)
export APIFY_API_TOKEN="your_apify_token_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# Run verification script
python verify_api_access.py
```

Expected output:
```
✅ Apify API connected! User: [your_username]
✅ Anthropic API connected! Model: claude-3-5-sonnet-20241022
✅ All API connections successful!
```

## 🚀 Next Steps After Setup

Once secrets are verified:

### 1. Test with Mock Analysis (No API Cost)

```bash
cd house-analysis
python test_complete_flow.py
```

This runs a complete analysis with mock data - no API calls, no costs.

### 2. Run Your First Real Analysis

Go to **Actions** → **Analyze House**:
- House ID: `test_001` (or any house from your Apify dataset)
- Apify Dataset ID: [your dataset ID]
- Rules version: `latest`
- LLM provider: `claude`

### 3. Check Results

After ~2-3 minutes, check:
- `houses/test_001/analyses/` - JSON analysis
- `houses/test_001/reports/` - HTML report

### 4. Integrate with Your Frontend

See `examples/spa-integration.html` for working integration code.

## 🔒 Security Notes

- ✅ Secrets are encrypted by GitHub
- ✅ Secrets are never exposed in logs
- ✅ Only workflows in this repo can access them
- ✅ You can rotate/update secrets anytime

## ⚠️ Troubleshooting

### "Secret not found" error
- Make sure secret names are exactly: `APIFY_API_TOKEN` and `ANTHROPIC_API_KEY`
- Check for typos in the names
- Verify secrets are added to the correct repository

### API connection fails
- Verify tokens are copied completely (no extra spaces)
- Check token hasn't expired
- Test with verification workflow first

### Workflow can't access secrets
- Ensure GitHub Actions is enabled in repository settings
- Check workflow has correct permissions
- Verify you're on the right branch

## 📞 Need Help?

1. Run the verification workflow first
2. Check workflow logs for detailed error messages
3. Test locally with `verify_api_access.py`
4. Review README.md for more troubleshooting tips

---

**Once secrets are added and verified, your House Analysis Agent Service is ready to use!** 🎉
