# Changelog

All notable changes to the House Analysis Agent Service will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-01-07

### Added
- Initial release of House Analysis Agent Service
- Versioned rules system with semantic versioning
- GitHub Actions workflows for async processing
  - Single house analysis workflow
  - Bulk re-analysis workflow
- Apify integration for data fetching and status updates
- LLM orchestrator with support for:
  - Mock LLM (for testing)
  - Claude API (Anthropic)
  - OpenAI API (GPT-4)
- HTML report generation with beautiful templates
- Complete audit trail in Git
- CLI tool for local testing
- Four analysis categories:
  - Location & Accessibility (25% weight)
  - Property Quality (30% weight)
  - Financial Potential (30% weight)
  - Legal & Compliance (15% weight)

### Rules Versions

#### v1.0.0 (2025-01-07)
- Initial rule set for short-stay rental analysis
- Four weighted categories
- Comprehensive criteria for each category
- Investment recommendation output (BUY/CONSIDER/PASS)

## [Next Version Ideas]

### Planned for v2.0.0
- Sustainability/ESG criteria category
- Market trends analysis
- Seasonal pricing optimization
- Guest demographic analysis
- Competitive positioning score

### Future Enhancements
- PDF report generation
- Webhook support for real-time updates
- Multi-language analysis support
- Comparative analysis (multiple houses)
- Historical trend tracking
- Rules A/B testing framework
- Cloudflare Worker for secure API key management
