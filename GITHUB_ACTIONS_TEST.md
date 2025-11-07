# Testing GitHub Actions Workflows

## Current Status

✅ Code is deployed to branch: `claude/house-analysis-agent-service-011CUuA9puUvKZPDXvAUDq5z`
✅ GitHub Secrets are configured (APIFY_API_TOKEN, ANTHROPIC_API_KEY)
❌ Apify token needs read permissions for datasets

## Test 1: Verify Secrets Workflow

This tests if your API keys are configured correctly.

### Using GitHub UI:

1. Go to: https://github.com/Saltbeef/frontend/actions
2. Click "Verify API Secrets" in the left sidebar
3. Click "Run workflow" dropdown
4. Select branch: `claude/house-analysis-agent-service-011CUuA9puUvKZPDXvAUDq5z`
5. Click green "Run workflow" button

Expected result:
```
✅ APIFY_API_TOKEN is set
✅ ANTHROPIC_API_KEY is set
✅ Apify API verified! (if token has permissions)
✅ Anthropic API verified!
```

### Using curl:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_PAT" \
  https://api.github.com/repos/Saltbeef/frontend/actions/workflows/verify_secrets.yml/dispatches \
  -d '{"ref":"claude/house-analysis-agent-service-011CUuA9puUvKZPDXvAUDq5z"}'
```

## Test 2: Full Analysis (When Apify is Fixed)

Once Apify token has read permissions:

### Using GitHub UI:

1. Go to: https://github.com/Saltbeef/frontend/actions
2. Click "Analyze House" workflow
3. Click "Run workflow"
4. Fill in:
   - **House ID**: Pick any ID from your Funda dataset
   - **Apify Dataset ID**: `Yb4fTMJ9wQsuyZf3L`
   - **Rules version**: `latest`
   - **LLM provider**: `claude`
5. Click "Run workflow"

Results will be in: `houses/{house-id}/`

### Using curl:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_PAT" \
  https://api.github.com/repos/Saltbeef/frontend/actions/workflows/analyze_house.yml/dispatches \
  -d '{
    "ref": "claude/house-analysis-agent-service-011CUuA9puUvKZPDXvAUDq5z",
    "inputs": {
      "house_id": "SOME_FUNDA_PROPERTY_ID",
      "apify_dataset_id": "Yb4fTMJ9wQsuyZf3L",
      "rules_version": "latest",
      "llm_provider": "claude"
    }
  }'
```

## Monitoring Workflow Runs

After triggering a workflow:

1. Go to Actions tab
2. You'll see your workflow running
3. Click on it to see live logs
4. Wait 2-3 minutes for completion
5. Check the `houses/` directory in your repo for results

## Expected Timeline

- Verification workflow: ~30 seconds
- Analysis workflow: ~2-3 minutes
- Mock local test: instant

## Next Steps After Successful Test

1. Merge branch to main (or your target branch)
2. Integrate trigger into your HTML frontend
3. Set up polling for status updates
4. Enjoy AI-powered house analysis! 🎉
