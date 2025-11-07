#!/usr/bin/env python3
"""
Command-line tool for analyzing houses locally.

Usage:
    python analyze.py --house-id abc123 --dataset-id xyz --rules v1.0.0
    python analyze.py --house-id abc123 --dataset-id xyz --mock
"""

import argparse
import json
import sys
from pathlib import Path

from src.agent import HouseAnalysisAgent
from src.apify_client import ApifyClient
from src.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description='Analyze a house for short-stay rental potential')

    parser.add_argument(
        '--house-id',
        required=True,
        help='Unique identifier for the house'
    )

    parser.add_argument(
        '--dataset-id',
        required=True,
        help='Apify dataset ID containing house data'
    )

    parser.add_argument(
        '--rules',
        default='latest',
        help='Rules version to use (default: latest)'
    )

    parser.add_argument(
        '--llm',
        choices=['mock', 'claude', 'openai'],
        default='mock',
        help='LLM provider to use (default: mock for testing)'
    )

    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock LLM (same as --llm mock)'
    )

    parser.add_argument(
        '--output',
        help='Output directory (default: houses/{house_id})'
    )

    parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Skip git commit'
    )

    args = parser.parse_args()

    # Override LLM if --mock flag is used
    if args.mock:
        args.llm = 'mock'

    print(f"🏠 Analyzing house: {args.house_id}")
    print(f"📊 Dataset: {args.dataset_id}")
    print(f"📋 Rules: {args.rules}")
    print(f"🤖 LLM: {args.llm}")
    print()

    try:
        # Step 1: Fetch house data
        print("1️⃣  Fetching house data from Apify...")
        client = ApifyClient()
        house_data = client.get_house_data(args.dataset_id, args.house_id)

        if not house_data:
            print(f"❌ House {args.house_id} not found in dataset {args.dataset_id}")
            return 1

        print(f"✅ House data fetched")
        print()

        # Step 2: Update status
        print("2️⃣  Updating Apify status...")
        client.update_analysis_status(
            dataset_id=args.dataset_id,
            house_id=args.house_id,
            status='processing'
        )
        print("✅ Status updated: processing")
        print()

        # Step 3: Run analysis
        print("3️⃣  Running analysis...")
        agent = HouseAnalysisAgent(
            rules_version=args.rules,
            llm_provider=args.llm
        )

        analysis = agent.analyze_house(
            house_data=house_data,
            house_id=args.house_id,
            apify_dataset_id=args.dataset_id
        )

        # Validate
        agent.validate_analysis(analysis)
        print(f"✅ Analysis complete - Score: {analysis['overall_score']}/10")
        print()

        # Step 4: Save results
        print("4️⃣  Saving results...")

        # Determine output directory
        if args.output:
            house_dir = Path(args.output)
        else:
            house_dir = Path('houses') / args.house_id

        house_dir.mkdir(parents=True, exist_ok=True)

        # Save analysis
        analyses_dir = house_dir / 'analyses'
        analyses_dir.mkdir(exist_ok=True)

        timestamp = analysis['analyzed_at'].replace(':', '-').split('.')[0]
        filename = f"{analysis['rules_version']}_{timestamp}.json"
        analysis_path = analyses_dir / filename

        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"   📄 Analysis: {analysis_path}")

        # Save raw data
        raw_dir = house_dir / 'raw'
        raw_dir.mkdir(exist_ok=True)
        raw_path = raw_dir / f'data_{timestamp}.json'

        with open(raw_path, 'w') as f:
            json.dump(house_data, f, indent=2)

        print(f"   📦 Raw data: {raw_path}")

        # Save latest reference
        with open(house_dir / 'latest_analysis.json', 'w') as f:
            json.dump({
                'analyzed_at': analysis['analyzed_at'],
                'rules_version': analysis['rules_version'],
                'overall_score': analysis['overall_score'],
                'analysis_file': str(analysis_path.relative_to(house_dir))
            }, f, indent=2)

        # Step 5: Generate HTML report
        print("5️⃣  Generating HTML report...")
        generator = ReportGenerator()
        reports_dir = house_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)

        report_path = reports_dir / f"{analysis['rules_version']}_{timestamp}.html"
        generator.save(analysis, report_path)

        print(f"   📊 Report: {report_path}")
        print()

        # Step 6: Update Apify
        print("6️⃣  Updating Apify status...")
        client.update_analysis_status(
            dataset_id=args.dataset_id,
            house_id=args.house_id,
            status='completed',
            score=analysis['overall_score']
        )
        print("✅ Status updated: completed")
        print()

        # Summary
        print("=" * 60)
        print("📈 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Overall Score: {analysis['overall_score']}/10")
        print(f"Recommendation: {analysis.get('investment_recommendation', 'N/A')}")
        print()
        print("Category Scores:")
        for cat_name, cat_data in analysis['category_scores'].items():
            print(f"  • {cat_name.replace('_', ' ').title()}: {cat_data['score']}/10")
        print()

        if analysis.get('top_concerns'):
            print("Top Concerns:")
            for concern in analysis['top_concerns'][:3]:
                print(f"  ⚠️  {concern}")
            print()

        print(f"📄 Full report: {report_path}")
        print()

        print("✨ Analysis complete!")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

        # Update Apify status to failed
        try:
            client.update_analysis_status(
                dataset_id=args.dataset_id,
                house_id=args.house_id,
                status='failed'
            )
        except:
            pass

        return 1


if __name__ == '__main__':
    sys.exit(main())
