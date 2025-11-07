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

            # Find the house by ID
            for item in items:
                # Assuming house data has an 'id' field
                # Adjust this based on actual Apify data structure
                if item.get("id") == house_id or item.get("house_id") == house_id:
                    return item

            print(f"House {house_id} not found in dataset {dataset_id}")
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
        Update house analysis status in Apify dataset.

        Note: This uses the Key-Value Store API since datasets are append-only.
        For persistent updates, you might need to use Apify's Key-Value Store
        or a custom API endpoint.

        Args:
            dataset_id: Apify dataset ID
            house_id: Unique identifier for the house
            status: Analysis status (pending, processing, completed, failed)
            score: Overall analysis score (0-10)
            analysis_url: URL to the analysis report

        Returns:
            True if update successful
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
            # Use default key-value store
            endpoint = f"key-value-stores/default/records/{store_key}"
            self._make_request("PUT", endpoint, data=update_data)
            print(f"Updated analysis status for house {house_id}: {status}")
            return True

        except Exception as e:
            print(f"Error updating analysis status: {e}")
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
