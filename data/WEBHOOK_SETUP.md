# Apify Webhook Setup

To automatically sync the Apify dataset when it updates, configure a webhook in Apify:

## Webhook Configuration

**URL:**
```
https://api.github.com/repos/Saltbeef/frontend/dispatches
```

**Method:**
```
POST
```

**Headers:**
```json
{
  "Accept": "application/vnd.github+json",
  "Authorization": "Bearer YOUR_GITHUB_TOKEN",
  "X-GitHub-Api-Version": "2022-11-28",
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "event_type": "apify_dataset_updated"
}
```

## GitHub Token Requirements

Create a GitHub Personal Access Token with permissions:
- `repo` (full control of private repositories)
- Or specifically: `repo:public_repo` for public repos + `workflow` to trigger actions

## Apify Integration Setup

1. Go to your Apify Actor/Task settings
2. Navigate to "Integrations" or "Webhooks"
3. Add a new webhook with "Run succeeded" event type
4. Use the URL, headers, and body above
5. Test the webhook

## Manual Sync

You can also manually trigger the sync:
- Go to Actions → "Sync Apify Dataset" → "Run workflow"
- Or via API: `gh workflow run sync_apify_dataset.yml`

## Automatic Backup

The workflow also runs every 6 hours as a backup sync mechanism.

## Files

- `data/apify_dataset.json` - Full dataset (all house listings)
- `data/analysis_scores.json` - Index of analyzed houses with scores
