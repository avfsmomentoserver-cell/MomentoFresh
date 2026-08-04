"""
Momento store for STRIDE.
Handles caching of raw data, STRIDE-compatible data, and forecasts.
"""
from typing import Dict, Optional, Any
import json


class MomentoStore:
    """Momento store for STRIDE data."""

    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.client = self._init_client()

    def _init_client(self):
        """Initialize the Momento client."""
        return None

    def store_raw_data(self, key: str, data: Dict[str, Any]) -> None:
        """Store raw data in Momento."""
        if self.client is None:
            print(f"[Mock] Storing raw data under key: {key}")
            return
        self.client.set(key, json.dumps(data))

    def retrieve_raw_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve raw data from Momento."""
        if self.client is None:
            return None
        cached_data = self.client.get(key)
        return json.loads(cached_data) if cached_data else None

    def store_stride_data(self, key: str, data: Dict[str, Any]) -> None:
        """Store STRIDE-compatible data in Momento."""
        if self.client is None:
            print(f"[Mock] Storing STRIDE data under key: stride:{key}")
            return
        self.client.set(f"stride:{key}", json.dumps(data))

    def retrieve_stride_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve STRIDE-compatible data from Momento."""
        if self.client is None:
            return None
        cached_data = self.client.get(f"stride:{key}")
        return json.loads(cached_data) if cached_data else None

    def store_and_convert(self, key: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store raw data and convert to STRIDE format."""
        from .stride.utils import convert_to_stride_format, preprocess_stride_data
        self.store_raw_data(key, raw_data)
        stride_data = convert_to_stride_format(raw_data)
        stride_data = preprocess_stride_data(stride_data)
        self.store_stride_data(key, stride_data)
        return stride_data

    def get_stride_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve STRIDE-compatible data, converting from raw if necessary."""
        from .stride.utils import convert_to_stride_format, preprocess_stride_data
        stride_data = self.retrieve_stride_data(key)
        if stride_data:
            return stride_data
        raw_data = self.retrieve_raw_data(key)
        if raw_data:
            stride_data = convert_to_stride_format(raw_data)
            stride_data = preprocess_stride_data(stride_data)
            self.store_stride_data(key, stride_data)
            return stride_data
        return None
