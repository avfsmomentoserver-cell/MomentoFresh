"""Utilities for STRIDE data conversion and preprocessing."""
from typing import Dict, Any


def convert_to_stride_format(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert raw Momento data to STRIDE-compatible format."""
    X = []
    for round_data in raw_data.get("rounds", []):
        if "multiplier" in round_data:
            X.append(float(round_data["multiplier"]))
    
    E = {"source": raw_data.get("source", "")}
    timestamps = [r.get("timestamp") for r in raw_data.get("rounds", [])]
    
    return {
        "X": X,
        "Y": [],
        "E": E,
        "metadata": {
            "collectedAt": raw_data.get("collectedAt"),
            "source": raw_data.get("source"),
            "timestamps": timestamps,
        },
    }


def preprocess_stride_data(stride_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add statistical features to STRIDE data."""
    X = stride_data["X"]
    if not X:
        return stride_data
    
    metadata = stride_data.get("metadata", {})
    metadata["mean"] = sum(X) / len(X)
    metadata["std"] = (sum((x - metadata["mean"]) ** 2 for x in X) / len(X)) ** 0.5
    metadata["min"] = min(X)
    metadata["max"] = max(X)
    stride_data["metadata"] = metadata
    return stride_data
