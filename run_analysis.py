#!/usr/bin/env python3
"""
Modern CLI tool for analyzing houses using compressed dataset and AirROI enrichment.

This script replaces the GitHub Action workflow for faster local iteration.
It uses the same logic as the workflow but runs locally with better feedback.

Usage:
    python run_analysis.py 43084820 --rules v2.0.0 --llm claude
    python run_analysis.py 43084820 --mock --no-commit
    python run_analysis.py 43084820 --skip-enrichment
"""

import json
import os
import subprocess
import sys
import time
import gzip
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import urllib.request
import urllib.error

try:
    import typer
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install typer rich")
    sys.exit(1)

# Import local modules
from src.agent import HouseAnalysisAgent
from src.report_generator import ReportGenerator
from src.markdown_generator import MarkdownGenerator

app = typer.Typer(
    help="Analyze houses for short-stay rental potential using compressed dataset",
    add_completion=False
)
console = Console()


def load_house_from_dataset(house_id: str) -> Optional[Dict[str, Any]]:
    """
    Extract house data from compressed dataset.

    Args:
        house_id: Unique house identifier (TinyId)

    Returns:
        House data dict or None if not found
    """
    dataset_path = Path('data/apify_dataset.json.gz')

    if not dataset_path.exists():
        console.print(f"[red]❌ Dataset not found: {dataset_path}[/red]")
        return None

    console.print(f"[dim]📦 Loading dataset: {dataset_path}[/dim]")

    try:
        with gzip.open(dataset_path, 'rt', encoding='utf-8') as f:
            dataset = json.load(f)

        # Find house by TinyId
        for item in dataset:
            if item.get('Identifiers', {}).get('TinyId') == house_id:
                console.print(f"[green]✅ House found in dataset[/green]")
                return item

        console.print(f"[red]❌ House {house_id} not found in dataset[/red]")
        return None

    except Exception as e:
        console.print(f"[red]❌ Error loading dataset: {e}[/red]")
        return None


def fetch_airroi_enrichment(
    house_id: str,
    house_data: Dict[str, Any],
    force: bool = False
) -> Dict[str, Any]:
    """
    Fetch enrichment data from AirROI API.

    Args:
        house_id: House identifier
        house_data: Raw house data
        force: Force re-fetch even if enrichment exists

    Returns:
        Enrichment data dict
    """
    enrichment_dir = Path('houses') / house_id / 'enrichment'
    enrichment_file = enrichment_dir / 'airroi_enrichment.json'

    # Check if enrichment already exists
    if enrichment_file.exists() and not force:
        console.print("[green]✅ Enrichment data already exists (use --force-enrichment to re-fetch)[/green]")
        with open(enrichment_file, 'r') as f:
            return json.load(f)

    # Create directory
    enrichment_dir.mkdir(parents=True, exist_ok=True)

    # Get API key
    api_key = os.getenv('AIRROI_API_KEY')
    if not api_key:
        console.print("[yellow]⚠️  No AirROI API key found (AIRROI_API_KEY)[/yellow]")
        enrichment = {'enriched': False, 'reason': 'No API key'}
        with open(enrichment_file, 'w') as f:
            json.dump(enrichment, f, indent=2)
        return enrichment

    console.print("[cyan]📡 Fetching enrichment data from AirROI API...[/cyan]")

    # Extract coordinates
    lat = house_data.get('AddressDetails', {}).get('Latitude')
    lon = house_data.get('AddressDetails', {}).get('Longitude')
    bedrooms = int(house_data.get('FastView', {}).get('NumberOfBedrooms', 2))
    city = house_data.get('AddressDetails', {}).get('City', '')
    postcode = house_data.get('AddressDetails', {}).get('PostCode', '')

    # Geocode if needed
    if not lat or not lon:
        if not postcode:
            console.print("[yellow]⚠️  No coordinates and no postcode, skipping enrichment[/yellow]")
            enrichment = {'enriched': False, 'reason': 'No coordinates or postcode'}
            with open(enrichment_file, 'w') as f:
                json.dump(enrichment, f, indent=2)
            return enrichment

        console.print(f"[dim]🗺️  Geocoding postcode {postcode}...[/dim]")
        try:
            time.sleep(1)  # Rate limit for Nominatim
            geocode_url = f"https://nominatim.openstreetmap.org/search?postalcode={postcode}&country=NL&format=json"
            req = urllib.request.Request(
                geocode_url,
                headers={'User-Agent': 'BNB-Analysis-Tool/1.0'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                geocode_results = json.loads(response.read().decode())

            if geocode_results:
                lat = float(geocode_results[0]['lat'])
                lon = float(geocode_results[0]['lon'])
                console.print(f"[green]  ✅ Geocoded to ({lat:.4f}, {lon:.4f})[/green]")
            else:
                console.print(f"[yellow]  ❌ Could not geocode postcode {postcode}[/yellow]")
                enrichment = {'enriched': False, 'reason': 'Geocoding failed'}
                with open(enrichment_file, 'w') as f:
                    json.dump(enrichment, f, indent=2)
                return enrichment

        except Exception as e:
            console.print(f"[yellow]  ❌ Geocoding error: {e}[/yellow]")
            enrichment = {'enriched': False, 'reason': f'Geocoding error: {str(e)}'}
            with open(enrichment_file, 'w') as f:
                json.dump(enrichment, f, indent=2)
            return enrichment

    # Prepare enrichment data
    enrichment = {
        'enriched': True,
        'enriched_at': datetime.now(timezone.utc).isoformat(),
        'house_id': house_id,
        'coordinates': {
            'latitude': lat,
            'longitude': lon,
            'source': 'original' if house_data.get('AddressDetails', {}).get('Latitude') else 'geocoded'
        },
        'api_calls': 0,
        'estimated_cost': 0.0
    }

    try:
        bathrooms = float(house_data.get('FastView', {}).get('NumberOfBathrooms', 1.0))
        guests = max(bedrooms * 2, 2)

        console.print(f"[dim]  Property: {bedrooms} bed, {bathrooms} bath, {guests} guests[/dim]")

        # 1. Fetch comparable listings
        console.print("[dim]  Fetching comparable listings...[/dim]")
        params = {
            'latitude': lat,
            'longitude': lon,
            'bedrooms': bedrooms,
            'baths': bathrooms,
            'guests': guests,
            'currency': 'native'
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        comparables_url = f"https://api.airroi.com/listings/comparables?{query_string}"

        req = urllib.request.Request(
            comparables_url,
            headers={'x-api-key': api_key}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            comparables_data = json.loads(response.read().decode())

        enrichment['comparables'] = comparables_data.get('data', [])
        enrichment['api_calls'] += 1
        enrichment['estimated_cost'] += 0.01

        console.print(f"[green]  ✅ Found {len(enrichment['comparables'])} comparable listings[/green]")

        # 2. Fetch revenue estimate
        console.print("[dim]  Fetching revenue estimate...[/dim]")
        estimate_params = {
            'lat': lat,
            'lng': lon,
            'bedrooms': bedrooms,
            'baths': bathrooms,
            'guests': guests,
            'currency': 'native'
        }
        estimate_query = '&'.join([f"{k}={v}" for k, v in estimate_params.items()])
        estimate_url = f"https://api.airroi.com/calculator/estimate?{estimate_query}"

        req = urllib.request.Request(
            estimate_url,
            headers={'x-api-key': api_key}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            revenue_estimate = json.loads(response.read().decode())

        enrichment['revenue_estimate'] = revenue_estimate.get('data', {})
        enrichment['api_calls'] += 1
        enrichment['estimated_cost'] += 0.01

        console.print(f"[green]  ✅ Revenue estimate fetched[/green]")

        console.print(f"[cyan]💰 API calls: {enrichment['api_calls']}, Cost: ${enrichment['estimated_cost']:.2f}[/cyan]")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        console.print(f"[red]❌ AirROI API Error {e.code}: {e.reason}[/red]")
        console.print(f"[dim]   Response: {error_body}[/dim]")
        enrichment['enriched'] = False
        enrichment['error'] = f"HTTP {e.code}: {e.reason}"
        enrichment['error_details'] = error_body
    except Exception as e:
        console.print(f"[red]❌ Error fetching enrichment: {e}[/red]")
        enrichment['enriched'] = False
        enrichment['error'] = str(e)

    # Save enrichment data
    with open(enrichment_file, 'w') as f:
        json.dump(enrichment, f, indent=2)

    console.print(f"[green]✅ Enrichment data saved to {enrichment_file}[/green]")
    return enrichment


def load_market_metrics(city: str) -> Optional[Dict[str, Any]]:
    """
    Load market metrics for a city.

    Args:
        city: City name

    Returns:
        Market metrics dict or None if not found
    """
    metrics_file = Path('data/market_metrics.json')

    if not metrics_file.exists():
        return None

    try:
        with open(metrics_file, 'r') as f:
            data = json.load(f)

        if city in data.get('cities', {}):
            console.print(f"[green]✅ Loaded market metrics for {city}[/green]")
            return data['cities'][city]
    except Exception as e:
        console.print(f"[yellow]⚠️  Error loading market metrics: {e}[/yellow]")

    return None


def update_analysis_scores(house_id: str, analysis: Dict[str, Any]) -> None:
    """
    Update the analysis scores index.

    Args:
        house_id: House identifier
        analysis: Analysis results
    """
    scores_file = Path('data/analysis_scores.json')

    # Load current scores
    if scores_file.exists():
        with open(scores_file, 'r') as f:
            scores_data = json.load(f)
    else:
        scores_data = {'last_updated': '', 'houses': {}}

    # Update
    scores_data['last_updated'] = datetime.now(timezone.utc).isoformat()
    scores_data['houses'][house_id] = {
        'score': analysis['overall_score'],
        'analyzed_at': analysis['analyzed_at'],
        'rules_version': analysis['rules_version']
    }

    # Save
    with open(scores_file, 'w') as f:
        json.dump(scores_data, f, indent=2)

    console.print(f"[green]✅ Updated analysis scores index[/green]")


def git_commit_and_push(house_id: str, score: float, rules_version: str) -> bool:
    """
    Commit and push analysis results to git.

    Args:
        house_id: House identifier
        score: Analysis score
        rules_version: Rules version used

    Returns:
        True if successful
    """
    try:
        # Add files
        subprocess.run(
            ['git', 'add', f'houses/{house_id}/', 'data/analysis_scores.json'],
            check=True,
            capture_output=True
        )

        # Check if there are changes
        result = subprocess.run(
            ['git', 'diff', '--staged', '--quiet'],
            capture_output=True
        )

        if result.returncode == 0:
            console.print("[dim]No changes to commit[/dim]")
            return True

        # Commit
        commit_msg = f"Analysis: {house_id} using {rules_version} (score: {score:.2f})"
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            check=True,
            capture_output=True
        )

        console.print(f"[green]✅ Committed: {commit_msg}[/green]")

        # Push
        console.print("[cyan]Pushing to remote...[/cyan]")
        subprocess.run(
            ['git', 'push', 'origin', 'main'],
            check=True,
            capture_output=True
        )

        console.print("[green]✅ Pushed to remote[/green]")
        return True

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Git error: {e}[/red]")
        if e.stderr:
            console.print(f"[dim]{e.stderr.decode()}[/dim]")
        return False


@app.command()
def analyze(
    house_id: str = typer.Argument(..., help="Unique house identifier (TinyId)"),
    rules_version: str = typer.Option("latest", "--rules", "-r", help="Rules version to use"),
    llm_provider: str = typer.Option("claude", "--llm", "-l", help="LLM provider (mock/claude/openai)"),
    mock: bool = typer.Option(False, "--mock", "-m", help="Use mock LLM (no API costs)"),
    skip_enrichment: bool = typer.Option(False, "--skip-enrichment", help="Skip AirROI enrichment"),
    force_enrichment: bool = typer.Option(False, "--force-enrichment", help="Force re-fetch enrichment data"),
    only_enrichment: bool = typer.Option(False, "--only-enrichment", help="Only fetch enrichment data, skip analysis"),
    no_commit: bool = typer.Option(False, "--no-commit", help="Skip git commit and push"),
    no_reports: bool = typer.Option(False, "--no-reports", help="Skip report generation"),
):
    """
    Analyze a house for short-stay rental potential.

    This script performs the same analysis as the GitHub Action workflow
    but runs locally for faster iteration and debugging.
    """

    # Override LLM if mock flag is set
    if mock:
        llm_provider = "mock"

    console.print()
    console.print("=" * 70)
    console.print(f"[bold cyan]🏠 House Analysis - ID: {house_id}[/bold cyan]")
    console.print("=" * 70)
    console.print(f"[dim]Rules: {rules_version} | LLM: {llm_provider}[/dim]")
    console.print()

    # Step 1: Load house data from compressed dataset
    console.print("[bold]1️⃣  Loading house data from dataset...[/bold]")
    house_data = load_house_from_dataset(house_id)

    if not house_data:
        console.print("[red]❌ Failed to load house data[/red]")
        raise typer.Exit(code=1)

    console.print()

    # Step 2: Fetch enrichment data
    if skip_enrichment and not only_enrichment:
        console.print("[bold]2️⃣  Skipping enrichment (--skip-enrichment)[/bold]")
        enrichment_data = None
    else:
        console.print("[bold]2️⃣  Fetching enrichment data...[/bold]")
        enrichment_data = fetch_airroi_enrichment(house_id, house_data, force=force_enrichment)

    console.print()

    # Early exit if only enrichment was requested
    if only_enrichment:
        console.print("[bold green]✨ Enrichment data fetched successfully![/bold green]")
        console.print(f"[dim]Saved to: houses/{house_id}/enrichment/airroi_enrichment.json[/dim]")
        console.print()

        if enrichment_data and enrichment_data.get('enriched'):
            console.print("[cyan]📊 Enrichment Summary:[/cyan]")
            console.print(f"  • API calls: {enrichment_data.get('api_calls', 0)}")
            console.print(f"  • Cost: ${enrichment_data.get('estimated_cost', 0):.2f}")
            console.print(f"  • Comparables found: {len(enrichment_data.get('comparables', []))}")
            console.print(f"  • Revenue estimate: {'✓' if enrichment_data.get('revenue_estimate') else '✗'}")
        console.print()
        return

    # Step 3: Load market metrics
    console.print("[bold]3️⃣  Loading market metrics...[/bold]")
    city = house_data.get('AddressDetails', {}).get('City')
    market_metrics = load_market_metrics(city) if city else None

    if not market_metrics:
        console.print("[dim]No market metrics found[/dim]")

    console.print()

    # Step 4: Run analysis
    console.print("[bold]4️⃣  Running analysis...[/bold]")

    agent = HouseAnalysisAgent(
        rules_version=rules_version,
        llm_provider=llm_provider
    )

    console.print(f"[dim]Agent initialized with {llm_provider} provider[/dim]")

    analysis = agent.analyze_house(
        house_data=house_data,
        house_id=house_id,
        apify_dataset_id='Yb4fTMJ9wQsuyZf3L',  # Hardcoded dataset ID
        enrichment_data=enrichment_data,
        market_metrics=market_metrics
    )

    # Validate
    agent.validate_analysis(analysis)

    console.print(f"[bold green]✅ Analysis complete - Score: {analysis['overall_score']:.2f}/10[/bold green]")
    console.print()

    # Step 5: Save analysis results
    console.print("[bold]5️⃣  Saving analysis results...[/bold]")

    house_dir = Path('houses') / house_id
    house_dir.mkdir(parents=True, exist_ok=True)

    # Save to analyses directory with version and timestamp
    analyses_dir = house_dir / 'analyses'
    analyses_dir.mkdir(exist_ok=True)

    timestamp = analysis['analyzed_at'].replace(':', '-').split('.')[0]
    filename = f"{analysis['rules_version']}_{timestamp}.json"
    analysis_path = analyses_dir / filename

    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    console.print(f"[green]  📄 {analysis_path}[/green]")

    # Save raw data
    raw_dir = house_dir / 'raw'
    raw_dir.mkdir(exist_ok=True)
    raw_path = raw_dir / f'data_{timestamp}.json'

    with open(raw_path, 'w') as f:
        json.dump(house_data, f, indent=2)

    console.print(f"[dim]  📦 {raw_path}[/dim]")

    # Save latest analysis reference
    with open(house_dir / 'latest_analysis.json', 'w') as f:
        json.dump({
            'analyzed_at': analysis['analyzed_at'],
            'rules_version': analysis['rules_version'],
            'overall_score': analysis['overall_score'],
            'analysis_file': str(analysis_path.relative_to(house_dir))
        }, f, indent=2)

    console.print()

    # Step 6: Generate reports
    if no_reports:
        console.print("[bold]6️⃣  Skipping report generation (--no-reports)[/bold]")
    else:
        console.print("[bold]6️⃣  Generating reports...[/bold]")

        reports_dir = house_dir / 'reports'
        reports_dir.mkdir(exist_ok=True)

        base_filename = f"{analysis['rules_version']}_{timestamp}"

        # HTML report
        html_generator = ReportGenerator()
        html_path = reports_dir / f'{base_filename}.html'
        html_generator.save(analysis, html_path)
        console.print(f"[green]  📊 {html_path}[/green]")

        # Markdown report
        md_generator = MarkdownGenerator()
        md_path = reports_dir / f'{base_filename}.md'
        md_generator.save(analysis, md_path)
        console.print(f"[green]  📝 {md_path}[/green]")

        # Create symlinks to latest reports
        latest_html = reports_dir / 'latest.html'
        latest_md = reports_dir / 'latest.md'

        # Remove old symlinks
        if latest_html.exists() or latest_html.is_symlink():
            latest_html.unlink()
        if latest_md.exists() or latest_md.is_symlink():
            latest_md.unlink()

        # Create new symlinks
        os.symlink(f'{base_filename}.html', latest_html)
        os.symlink(f'{base_filename}.md', latest_md)

        console.print(f"[dim]  🔗 Created symlinks to latest reports[/dim]")

    console.print()

    # Step 7: Update analysis scores index
    console.print("[bold]7️⃣  Updating analysis scores index...[/bold]")
    update_analysis_scores(house_id, analysis)
    console.print()

    # Step 8: Git commit and push
    if no_commit:
        console.print("[bold]8️⃣  Skipping git commit (--no-commit)[/bold]")
    else:
        console.print("[bold]8️⃣  Committing and pushing to git...[/bold]")
        git_commit_and_push(house_id, analysis['overall_score'], rules_version)

    console.print()

    # Summary
    console.print("=" * 70)
    console.print("[bold cyan]📈 ANALYSIS SUMMARY[/bold cyan]")
    console.print("=" * 70)
    console.print(f"[bold]Overall Score:[/bold] {analysis['overall_score']:.2f}/10")
    console.print(f"[bold]Recommendation:[/bold] {analysis.get('investment_recommendation', 'N/A')}")
    console.print()

    console.print("[bold]Category Scores:[/bold]")
    for cat_name, cat_data in analysis['category_scores'].items():
        score = cat_data['score']
        color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
        console.print(f"  • {cat_name.replace('_', ' ').title()}: [{color}]{score:.1f}/10[/{color}]")
    console.print()

    if analysis.get('top_concerns'):
        console.print("[bold]Top Concerns:[/bold]")
        for concern in analysis['top_concerns'][:3]:
            console.print(f"  [yellow]⚠️  {concern}[/yellow]")
        console.print()

    if not no_reports:
        console.print(f"[bold]📄 Full report:[/bold] {reports_dir / 'latest.html'}")
        console.print()

    console.print("[bold green]✨ Analysis complete![/bold green]")
    console.print()


if __name__ == '__main__':
    app()
