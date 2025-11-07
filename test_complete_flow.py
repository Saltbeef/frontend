#!/usr/bin/env python3
"""
Complete flow test for the House Analysis Agent Service.

This script demonstrates the entire analysis pipeline:
1. Mock house data creation
2. Analysis with mock LLM
3. Report generation
4. File structure verification

Run: python test_complete_flow.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import HouseAnalysisAgent
from src.report_generator import ReportGenerator
from rules import get_rules, RulesRegistry


def create_mock_house_data():
    """Create realistic mock house data."""
    return {
        "id": "test_demo_001",
        "title": "Beautiful Canal View Apartment in Amsterdam Center",
        "url": "https://example.com/listing/test_demo_001",
        "scraped_at": datetime.now().isoformat(),

        "basic_info": {
            "description": "Luxurious 2-bedroom apartment with stunning canal views. "
                         "Perfect for short-stay rentals. Recently renovated with modern amenities. "
                         "Located in the heart of Amsterdam's historic Jordaan neighborhood.",
            "property_type": "Apartment",
            "listing_type": "Entire place"
        },

        "location": {
            "address": "Prinsengracht 123, Amsterdam",
            "city": "Amsterdam",
            "neighborhood": "Jordaan",
            "coordinates": {"lat": 52.3738, "lng": 4.8832},
            "nearby_attractions": [
                "Anne Frank House (5 min walk)",
                "Dam Square (10 min walk)",
                "Central Station (15 min walk)"
            ],
            "transport": {
                "nearest_tram": "Tram 13, 17 - 2 min walk",
                "airport_distance_km": 18
            }
        },

        "property_details": {
            "bedrooms": 2,
            "bathrooms": 1,
            "max_guests": 4,
            "square_meters": 75,
            "floor": 2,
            "has_elevator": False,
            "last_renovated": 2023
        },

        "amenities": [
            "WiFi", "Kitchen", "Heating", "Washer", "Dryer",
            "TV", "Balcony", "Canal view"
        ],

        "pricing": {
            "currency": "EUR",
            "base_price_per_night": 150,
            "weekend_price_per_night": 180,
            "cleaning_fee": 50,
            "minimum_stay_nights": 2
        },

        "ratings": {
            "overall_rating": 4.8,
            "number_of_reviews": 127,
            "rating_breakdown": {
                "cleanliness": 4.9,
                "location": 4.9,
                "value": 4.6
            }
        },

        "host_info": {
            "host_name": "Jan",
            "host_since": "2018-03-15",
            "response_rate": 98,
            "is_superhost": True
        },

        "legal_compliance": {
            "registration_number": "0363A12345678",
            "license_verified": True,
            "max_nights_per_year": 60
        },

        "competition_analysis": {
            "similar_listings_in_area": 45,
            "average_price_in_area": 145
        }
    }


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_complete_flow():
    """Run complete analysis flow test."""
    print_section("🏠 House Analysis Agent Service - Complete Flow Test")

    # Step 1: Show available rules
    print_section("1️⃣  Available Rules Versions")
    versions = RulesRegistry.list_versions()
    print(f"✅ Available versions: {versions}")

    # Load rules
    rules = get_rules('v1.0.0')
    print(f"✅ Loaded rules: {rules.version}")
    print(f"✅ Categories: {list(rules.categories.keys())}")
    print(f"✅ Category weights:")
    for name, criteria in rules.categories.items():
        print(f"   • {criteria.name}: {criteria.weight * 100}%")

    # Step 2: Create mock data
    print_section("2️⃣  Creating Mock House Data")
    house_data = create_mock_house_data()
    house_id = house_data['id']
    print(f"✅ Created mock house: {house_id}")
    print(f"   • Title: {house_data['title']}")
    print(f"   • Location: {house_data['location']['address']}")
    print(f"   • Price: €{house_data['pricing']['base_price_per_night']}/night")
    print(f"   • Bedrooms: {house_data['property_details']['bedrooms']}")
    print(f"   • Rating: {house_data['ratings']['overall_rating']}/5.0")

    # Step 3: Initialize agent
    print_section("3️⃣  Initializing Analysis Agent")
    agent = HouseAnalysisAgent(
        rules_version='v1.0.0',
        llm_provider='mock'  # Using mock to avoid API costs
    )
    print(f"✅ Agent initialized with {agent.llm_provider} LLM")
    print(f"✅ Using rules version: {agent.rules.version}")

    # Step 4: Run analysis
    print_section("4️⃣  Running Analysis")
    print("⏳ Analyzing house (this may take a moment)...")

    analysis = agent.analyze_house(
        house_data=house_data,
        house_id=house_id,
        apify_dataset_id='test_dataset'
    )

    print(f"✅ Analysis complete!")
    print(f"   • Overall score: {analysis['overall_score']}/10")
    print(f"   • Processing time: {analysis['metadata']['processing_time_seconds']}s")

    # Step 5: Validate analysis
    print_section("5️⃣  Validating Analysis")
    try:
        agent.validate_analysis(analysis)
        print("✅ Analysis validation passed")
    except ValueError as e:
        print(f"❌ Validation failed: {e}")
        return False

    # Step 6: Show category scores
    print_section("6️⃣  Category Scores")
    for cat_name, cat_data in analysis['category_scores'].items():
        print(f"\n{cat_name.upper()}: {cat_data['score']}/10")
        print(f"  Reasoning: {cat_data['reasoning'][:100]}...")
        if cat_data.get('red_flags'):
            print(f"  🚩 Red flags: {len(cat_data['red_flags'])}")
        if cat_data.get('recommendations'):
            print(f"  💡 Recommendations: {len(cat_data['recommendations'])}")

    # Step 7: Save results
    print_section("7️⃣  Saving Results")

    # Create test output directory
    test_dir = Path('test_output') / house_id
    test_dir.mkdir(parents=True, exist_ok=True)

    # Save analysis JSON
    analyses_dir = test_dir / 'analyses'
    analyses_dir.mkdir(exist_ok=True)

    timestamp = analysis['analyzed_at'].replace(':', '-').split('.')[0]
    analysis_file = analyses_dir / f"v1.0.0_{timestamp}.json"

    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"✅ Analysis saved: {analysis_file}")

    # Save raw data
    raw_dir = test_dir / 'raw'
    raw_dir.mkdir(exist_ok=True)
    raw_file = raw_dir / f"data_{timestamp}.json"

    with open(raw_file, 'w') as f:
        json.dump(house_data, f, indent=2)

    print(f"✅ Raw data saved: {raw_file}")

    # Step 8: Generate HTML report
    print_section("8️⃣  Generating HTML Report")

    generator = ReportGenerator()
    reports_dir = test_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / f"v1.0.0_{timestamp}.html"

    generator.save(analysis, str(report_file))
    print(f"✅ HTML report generated: {report_file}")

    # Step 9: Summary
    print_section("9️⃣  Test Summary")
    print(f"✅ All tests passed!")
    print(f"\n📊 Analysis Results:")
    print(f"   • Overall Score: {analysis['overall_score']}/10")
    print(f"   • Recommendation: {analysis.get('investment_recommendation', 'N/A')}")
    print(f"\n📁 Output Files:")
    print(f"   • Analysis JSON: {analysis_file}")
    print(f"   • HTML Report: {report_file}")
    print(f"   • Raw Data: {raw_file}")
    print(f"\n🌐 View Report:")
    print(f"   Open in browser: file://{report_file.absolute()}")

    # Show top strengths and concerns
    if analysis.get('top_strengths'):
        print(f"\n💪 Top Strengths:")
        for strength in analysis['top_strengths'][:3]:
            print(f"   • {strength}")

    if analysis.get('top_concerns'):
        print(f"\n⚠️  Top Concerns:")
        for concern in analysis['top_concerns'][:3]:
            print(f"   • {concern}")

    print_section("✨ Test Complete!")
    return True


if __name__ == '__main__':
    try:
        success = test_complete_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
