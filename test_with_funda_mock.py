#!/usr/bin/env python3
"""
Test with mock Funda.nl property data.

This simulates what a real Funda property analysis would look like.
Run: python test_with_funda_mock.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent import HouseAnalysisAgent
from src.report_generator import ReportGenerator


def create_funda_mock_property():
    """Create realistic Funda.nl property mock data."""
    return {
        "id": "funda_amsterdam_001",
        "url": "https://www.funda.nl/koop/amsterdam/appartement-12345/",

        # Basic info
        "title": "Ruim 3-kamerappartement met balkon in De Pijp",
        "description": """
        Prachtig gerenoveerd 3-kamerappartement van circa 75m² met zonnig balkon
        op het zuiden, gelegen in het bruisende Amsterdam Zuid. De woning beschikt
        over 2 ruime slaapkamers, moderne keuken en badkamer, en ligt op loopafstand
        van alle voorzieningen.
        """,
        "property_type": "Appartement",

        # Location
        "address": "Van Woustraat 123",
        "postal_code": "1073 LN",
        "city": "Amsterdam",
        "neighborhood": "De Pijp",
        "coordinates": {
            "lat": 52.3547,
            "lng": 4.8927
        },

        # Property details
        "asking_price": 475000,
        "price_per_m2": 6333,
        "living_area_m2": 75,
        "plot_area_m2": None,
        "rooms": 3,
        "bedrooms": 2,
        "bathrooms": 1,
        "floors": 1,
        "floor_location": "2e verdieping",
        "elevator": False,

        # Building info
        "year_built": 1920,
        "building_type": "Bovenwoning",
        "monument": False,
        "insulation": ["Dubbelglas", "Dakisolatie"],

        # Energy
        "energy_label": "C",
        "energy_label_provisional": False,

        # Features
        "balcony": True,
        "balcony_orientation": "Zuid",
        "garden": False,
        "parking": "Betaald parkeren op straat",
        "storage": True,

        # Financial
        "vve": True,
        "vve_contribution_monthly": 125,
        "property_tax_municipal": 800,  # per year
        "ground_lease": False,

        # Status
        "status": "Te koop",
        "acceptance": "In overleg",
        "days_on_market": 12,

        # Nearby (distances in meters)
        "nearby": {
            "albert_cuyp_markt": 300,
            "sarphatipark": 400,
            "metro_station": 600,
            "tram_stop": 150,
            "supermarket": 200,
            "schools": 350,
            "restaurants": 100
        },

        # Transport
        "transport": {
            "metro": "Noord/Zuidlijn - Station De Pijp (600m)",
            "tram": "Lijn 3, 12, 24 (150m)",
            "train": "Amsterdam Centraal (15 min)",
            "airport": "Schiphol (25 min met trein)"
        },

        # Rental potential (for short-stay analysis)
        "rental_potential": {
            "estimated_market_rent_monthly": 1800,
            "comparable_rentals": [1750, 1850, 1900],
            "short_stay_allowed": True,  # Check with VVE
            "short_stay_license_required": True,
            "tourist_area": True
        },

        # Agent info
        "broker": {
            "name": "Makelaardij Amsterdam",
            "phone": "020-1234567",
            "listed_date": "2025-10-26"
        },

        # Photos
        "photo_count": 32,
        "photos": [
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg"
        ],

        # Additional notes
        "notes": """
        - Recent renovation (2023)
        - Modern kitchen with appliances
        - Bathroom with walk-in shower
        - High ceilings (3.2m)
        - Original details preserved
        - Active VVE with maintenance plan
        - Popular neighborhood with high demand
        - Close to Amstel river and Sarphatipark
        """
    }


def main():
    print("=" * 70)
    print("  🇳🇱 Funda.nl Property Analysis - Mock Test")
    print("=" * 70)
    print()

    # Create mock Funda property
    print("📊 Creating mock Funda property...")
    property_data = create_funda_mock_property()

    print(f"✅ Property: {property_data['title']}")
    print(f"   📍 Location: {property_data['address']}, {property_data['city']}")
    print(f"   💰 Price: €{property_data['asking_price']:,}")
    print(f"   📐 Size: {property_data['living_area_m2']}m²")
    print(f"   🛏️  Rooms: {property_data['rooms']} ({property_data['bedrooms']} bedrooms)")
    print()

    # Initialize agent
    print("🤖 Initializing analysis agent...")
    agent = HouseAnalysisAgent(
        rules_version='v1.0.0',
        llm_provider='mock'  # Using mock for now
    )
    print("✅ Agent ready")
    print()

    # Run analysis
    print("🔍 Analyzing property...")
    analysis = agent.analyze_house(
        house_data=property_data,
        house_id=property_data['id'],
        apify_dataset_id='funda-properties'
    )

    print(f"✅ Analysis complete!")
    print(f"   📊 Overall Score: {analysis['overall_score']}/10")
    print()

    # Show category scores
    print("📋 Category Breakdown:")
    for cat_name, cat_data in analysis['category_scores'].items():
        print(f"   {cat_name.title():20s}: {cat_data['score']:.1f}/10")
    print()

    # Save results
    print("💾 Saving results...")
    output_dir = Path('test_output') / property_data['id']
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save analysis JSON
    analyses_dir = output_dir / 'analyses'
    analyses_dir.mkdir(exist_ok=True)

    timestamp = analysis['analyzed_at'].replace(':', '-').split('.')[0]
    analysis_file = analyses_dir / f"v1.0.0_{timestamp}.json"

    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"   ✅ Analysis: {analysis_file}")

    # Generate HTML report
    print("📄 Generating HTML report...")
    generator = ReportGenerator()
    reports_dir = output_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)

    report_file = reports_dir / f"v1.0.0_{timestamp}.html"
    generator.save(analysis, str(report_file))

    print(f"   ✅ Report: {report_file}")
    print()

    # Summary
    print("=" * 70)
    print("  ✨ Analysis Complete!")
    print("=" * 70)
    print()
    print(f"📊 Score: {analysis['overall_score']}/10")
    print(f"💡 Recommendation: {analysis.get('investment_recommendation', 'N/A')[:50]}...")
    print()
    print(f"🌐 View report: file://{report_file.absolute()}")
    print()

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
