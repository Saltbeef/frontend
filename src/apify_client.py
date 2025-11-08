"""Apify API client for fetching house data and updating analysis results."""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse


class ApifyClient:
    """Client for interacting with Apify API."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Apify client.

        Args:
            api_token: Apify API token. If not provided, reads from APIFY_API_TOKEN env var.
        """
        self.api_token = api_token or os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "Apify API token required. Set APIFY_API_TOKEN environment variable."
            )

        self.base_url = "https://api.apify.com/v2"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Apify API.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            data: Optional request body data

        Returns:
            Response JSON data

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Add token to URL
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}token={self.api_token}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read()
                return json.loads(response_data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(
                f"Apify API request failed: {e.code} {e.reason}\n{error_body}"
            )
        except urllib.error.URLError as e:
            raise Exception(f"Network error connecting to Apify: {e.reason}")

    def get_house_data(
        self,
        dataset_id: str,
        house_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch house data from Apify dataset.

        Args:
            dataset_id: Apify dataset ID
            house_id: Unique identifier for the house

        Returns:
            House data dictionary or None if not found
        """
        endpoint = f"datasets/{dataset_id}/items"

        try:
            response = self._make_request("GET", endpoint)
            items = response if isinstance(response, list) else response.get("data", [])

            # Possible ID fields to check (common patterns in Funda/property datasets)
            id_fields = [
                "id",
                "house_id",
                "globalId",
                "makelaarId",
                "objectId",
                "propertyId",
                "advertentieId",
                "internalId"
            ]

            print(f"🔍 Searching for house {house_id} in dataset {dataset_id}")
            print(f"   Dataset contains {len(items)} items")

            # Find the house by checking multiple possible ID fields
            for idx, item in enumerate(items):
                # Check all possible ID fields
                for field in id_fields:
                    field_value = item.get(field)
                    if field_value is not None:
                        # Try both string and integer comparison
                        if str(field_value) == str(house_id):
                            print(f"✅ Found house using field '{field}' = {field_value}")
                            return item

                # Also check if the ID appears in the URL
                url = item.get("url", "")
                if house_id in str(url):
                    print(f"✅ Found house by URL match: {url}")
                    return item

            # If not found, show debugging information
            print(f"❌ House {house_id} not found in dataset {dataset_id}")
            print(f"\n📋 Sample data structure from first item:")
            if items:
                sample = items[0]
                available_fields = list(sample.keys())
                print(f"   Available fields: {', '.join(available_fields[:20])}")

                # Show ID-like fields and their values
                print(f"\n   ID-like fields in first item:")
                for field in available_fields:
                    if any(keyword in field.lower() for keyword in ['id', 'code', 'number', 'ref']):
                        value = sample.get(field)
                        print(f"     - {field}: {value}")

                # Show URL if available
                if 'url' in sample:
                    print(f"     - url: {sample.get('url')}")

            print(f"\n💡 Tip: Check Apify Console at:")
            print(f"   https://console.apify.com/storage/datasets/{dataset_id}")

            return None

        except Exception as e:
            print(f"Error fetching house data: {e}")
            raise

    def update_analysis_status(
        self,
        dataset_id: str,
        house_id: str,
        status: str,
        score: Optional[float] = None,
        analysis_url: Optional[str] = None
    ) -> bool:
        """
        Update house analysis status in Apify Key-Value Store.

        Note: This is optional status tracking. If the Key-Value Store doesn't exist,
        a warning is logged but the operation doesn't fail.

        Args:
            dataset_id: Apify dataset ID
            house_id: Unique identifier for the house
            status: Analysis status (pending, processing, completed, failed)
            score: Overall analysis score (0-10)
            analysis_url: URL to the analysis report

        Returns:
            True if update successful, False otherwise (non-critical)
        """
        # Store analysis summary in Key-Value Store
        # Format: analysis_{house_id}
        store_key = f"analysis_{house_id}"

        update_data = {
            "house_id": house_id,
            "status": status,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

        if score is not None:
            update_data["score"] = score

        if analysis_url:
            update_data["analysis_url"] = analysis_url

        try:
            # Try to create Key-Value Store if it doesn't exist
            try:
                self._make_request("POST", "key-value-stores", data={"name": "default"})
                print(f"Created default Key-Value Store")
            except Exception as create_error:
                # Store might already exist, that's fine
                if "already exists" not in str(create_error).lower() and "409" not in str(create_error):
                    print(f"Note: Could not create Key-Value Store (may already exist): {create_error}")

            # Use default key-value store
            endpoint = f"key-value-stores/default/records/{store_key}"
            self._make_request("PUT", endpoint, data=update_data)
            print(f"✅ Updated analysis status for house {house_id}: {status}")
            return True

        except Exception as e:
            # This is non-critical - analysis results are saved to Git anyway
            print(f"⚠️  Could not update Apify status (non-critical): {e}")
            print(f"   Analysis results are still saved to Git repository")
            return False

    def get_analysis_status(
        self,
        house_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current analysis status for a house.

        Args:
            house_id: Unique identifier for the house

        Returns:
            Status data or None if not found
        """
        store_key = f"analysis_{house_id}"

        try:
            endpoint = f"key-value-stores/default/records/{store_key}"
            return self._make_request("GET", endpoint)
        except Exception as e:
            if "404" in str(e):
                return None
            print(f"Error fetching analysis status: {e}")
            raise


def get_client() -> ApifyClient:
    """Convenience function to get an initialized Apify client."""
    return ApifyClient()
