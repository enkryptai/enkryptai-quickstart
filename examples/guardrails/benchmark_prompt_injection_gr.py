"""
Benchmark Enkrypt AI Guardrails against Prompt Injection Dataset

This script:
1. Loads a prompt injection dataset (supports multiple formats)
2. Runs each text through Enkrypt AI guardrails
3. Calculates metrics: Accuracy, Precision, Recall, F1

Supported dataset formats:
- Format 1: text (str), label (str: "jailbreak" or "benign")
- Format 2: prompt (str), is_jailbreak (bool)
"""

import os
import json
import time
import requests
from datetime import datetime
from datasets import load_dataset
from dotenv import load_dotenv
from typing import Tuple, Optional, Dict, List, Callable
from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from abc import ABC, abstractmethod

load_dotenv()


# Get tokens from environment variables
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
API_KEY = os.getenv("ENKRYPTAI_API_KEY")


class DatasetAdapter(ABC):
    """
    Abstract base class for dataset adapters.
    Provides a unified interface for accessing different dataset formats.
    """
    
    @abstractmethod
    def get_text(self, index: int) -> str:
        """Get the text/prompt at the given index."""
        pass
    
    @abstractmethod
    def get_label(self, index: int) -> Tuple[int, str]:
        """
        Get the label at the given index.
        
        Returns:
            Tuple of (binary_label: int, label_str: str)
            binary_label: 1 for jailbreak, 0 for benign
            label_str: "jailbreak" or "benign"
        """
        pass
    
    @abstractmethod
    def get_length(self) -> int:
        """Get the total number of samples in the dataset."""
        pass


class TextLabelStringAdapter(DatasetAdapter):
    """
    Adapter for datasets with text and label as string ("jailbreak" or "benign").
    Format: text (str), label (str: "jailbreak" or "benign")
    """
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.texts = dataset['text']
        self.labels = dataset['label']
    
    def get_text(self, index: int) -> str:
        return self.texts[index] if index < len(self.texts) else ""
    
    def get_label(self, index: int) -> Tuple[int, str]:
        label = self.labels[index] if index < len(self.labels) else ""
        true_label = 1 if label.lower() == "jailbreak" else 0
        true_label_str = "jailbreak" if true_label == 1 else "benign"
        return true_label, true_label_str
    
    def get_length(self) -> int:
        return len(self.dataset)


class PromptIsJailbreakAdapter(DatasetAdapter):
    """
    Adapter for datasets with prompt and is_jailbreak boolean fields.
    Format: prompt (str), is_jailbreak (bool)
    """
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.prompts = dataset['prompt']
        self.is_jailbreak = dataset['is_jailbreak']
    
    def get_text(self, index: int) -> str:
        return self.prompts[index] if index < len(self.prompts) else ""
    
    def get_label(self, index: int) -> Tuple[int, str]:
        is_jb = self.is_jailbreak[index] if index < len(self.is_jailbreak) else False
        true_label = 1 if is_jb else 0
        true_label_str = "jailbreak" if true_label == 1 else "benign"
        return true_label, true_label_str
    
    def get_length(self) -> int:
        return len(self.dataset)


class TextLabelIntAdapter(DatasetAdapter):
    """
    Adapter for datasets with text and label as integer (0 or 1).
    Format: text (str), label (int64: 0 or 1)
    """
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.texts = dataset['text']
        self.labels = dataset['label']
    
    def get_text(self, index: int) -> str:
        return self.texts[index] if index < len(self.texts) else ""
    
    def get_label(self, index: int) -> Tuple[int, str]:
        label = self.labels[index] if index < len(self.labels) else 0
        # Convert to int if it's not already (handles numpy int64, etc.)
        true_label = int(label)
        true_label_str = "jailbreak" if true_label == 1 else "benign"
        return true_label, true_label_str
    
    def get_length(self) -> int:
        return len(self.dataset)


# Registry of available dataset adapters
DATASET_ADAPTERS = {
    "promptIsJailbreak": PromptIsJailbreakAdapter,
    "textLabelString": TextLabelStringAdapter,
    "textLabelInt": TextLabelIntAdapter,
}


def create_dataset_adapter(dataset, adapter_name: Optional[str] = None) -> DatasetAdapter:
    """
    Factory function to create the appropriate dataset adapter.
    
    Args:
        dataset: HuggingFace dataset object
        adapter_name: Optional name of the adapter to use (e.g., "qualifire", "guardrailsAI").
                     If None, will auto-detect based on dataset structure.
        
    Returns:
        DatasetAdapter instance
        
    Raises:
        ValueError: If adapter_name is specified but not found, or if auto-detection fails
    """
    # If adapter name is explicitly provided, use it
    if adapter_name is not None:
        adapter_name_lower = adapter_name.lower()
        if adapter_name_lower not in DATASET_ADAPTERS:
            available = ', '.join(DATASET_ADAPTERS.keys())
            raise ValueError(
                f"Unknown adapter name '{adapter_name}'. "
                f"Available adapters: {available}"
            )
        adapter_class = DATASET_ADAPTERS[adapter_name_lower]
        return adapter_class(dataset)
    
    # Otherwise, auto-detect based on dataset structure
    # Check for prompt + is_jailbreak format
    if 'prompt' in dataset.column_names and 'is_jailbreak' in dataset.column_names:
        return PromptIsJailbreakAdapter(dataset)
    
    # Check for text + label format
    elif 'text' in dataset.column_names and 'label' in dataset.column_names:
        # Check if label is integer type (0/1) or string type ("jailbreak"/"benign")
        if len(dataset) > 0:
            sample_label = dataset['label'][0]
            sample_text = dataset['text'][0]
            # Ensure text is a string
            if not isinstance(sample_text, str):
                raise ValueError(
                    f"Expected 'text' to be a string but got type '{type(sample_text).__name__}'"
                )
            # secure type checking for int
            if isinstance(sample_label, int):
                return TextLabelIntAdapter(dataset)

            # Accept int-like np.integer or pandas types, but not bool
            if hasattr(sample_label, "__int__") and not isinstance(sample_label, bool) and type(sample_label).__name__ != "str":
                try:
                    if isinstance(int(sample_label), int):
                        return TextLabelIntAdapter(dataset)
                except Exception:
                    pass
            # Otherwise, assume string labels (or catch-all fallback)
            return TextLabelStringAdapter(dataset)
    
    else:
        available_cols = ', '.join(dataset.column_names)
        available_adapters = ', '.join(DATASET_ADAPTERS.keys())
        raise ValueError(
            f"Could not auto-detect dataset format. Available columns: {available_cols}. "
            f"Please specify adapter_name explicitly. Available adapters: {available_adapters}"
        )


def call_guardrails_api(text: str) -> Tuple[dict, float]:
    """
    Call Enkrypt AI guardrails API to detect injection attacks.
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (JSON response from the API, latency in seconds)
    """
    url = "https://api.enkryptai.com/guardrails/detect"
    
    payload = json.dumps({
        "text": text,
        "detectors": {
            "injection_attack": {
                "enabled": True
            }
        }
    })
    
    headers = {
        'Content-Type': 'application/json',
        'apikey': API_KEY
    }
    
    start_time = time.time()
    response = requests.request("POST", url, headers=headers, data=payload)
    latency = time.time() - start_time
    
    response.raise_for_status()
    
    json_response = json.loads(response.text)
    return json_response, latency


def parse_for_attacks(guardrails_response: dict) -> bool:
    """
    Parse a guardrails response to check for injection attacks.
    
    Args:
        guardrails_response: JSON dict from API call
        
    Returns:
        bool: True if injection_attack == 1, False otherwise
    """
    summary = guardrails_response.get("summary", {})
    return summary.get("injection_attack", 0) == 1


def calculate_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """
    Calculate Accuracy, Precision, Recall, and F1 score using scikit-learn.
    
    Args:
        y_true: List of true labels (1 for jailbreak, 0 for benign)
        y_pred: List of predicted labels (1 for injection detected, 0 for benign)
        
    Returns:
        Dictionary with accuracy, precision, recall, and f1 scores
    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }


def calculate_confusion_matrix_values(y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
    """
    Calculate confusion matrix values using scikit-learn.
    
    Args:
        y_true: List of true labels (1 for jailbreak, 0 for benign)
        y_pred: List of predicted labels (1 for injection detected, 0 for benign)
        
    Returns:
        Dictionary with tp, tn, fp, fn values
    """
    cm = confusion_matrix(y_true, y_pred)
    # For binary classification: cm[0,0]=TN, cm[0,1]=FP, cm[1,0]=FN, cm[1,1]=TP
    tn, fp, fn, tp = cm.ravel()
    
    return {
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn)
    }


def calculate_latency_stats(detailed_results: List[Dict]) -> Dict[str, Optional[float]]:
    """
    Calculate latency statistics from detailed results.
    
    Args:
        detailed_results: List of result dictionaries with latency_ms field
        
    Returns:
        Dictionary with average_ms, min_ms, max_ms
    """
    latencies = [r["latency_ms"] for r in detailed_results if r["latency_ms"] is not None]
    
    if not latencies:
        return {
            "average_ms": None,
            "min_ms": None,
            "max_ms": None
        }
    
    return {
        "average_ms": round(sum(latencies) / len(latencies), 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2)
    }


def display_results(metrics: Dict[str, float], cm: Dict[str, int], latency_stats: Dict[str, Optional[float]]):
    """
    Display benchmark results to console.
    
    Args:
        metrics: Dictionary with accuracy, precision, recall, f1
        cm: Dictionary with confusion matrix values (tp, tn, fp, fn)
        latency_stats: Dictionary with latency statistics
    """
    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    
    print(f"\nConfusion Matrix:")
    print(f"  True Positives (TP):  {cm['tp']}")
    print(f"  True Negatives (TN):  {cm['tn']}")
    print(f"  False Positives (FP): {cm['fp']}")
    print(f"  False Negatives (FN): {cm['fn']}")
    
    print(f"\nMetrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"  Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"  Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"  F1 Score:  {metrics['f1']:.4f} ({metrics['f1']*100:.2f}%)")
    
    if latency_stats["average_ms"] is not None:
        print(f"\nLatency Statistics:")
        print(f"  Average: {latency_stats['average_ms']:.2f} ms")
        print(f"  Min:     {latency_stats['min_ms']:.2f} ms")
        print(f"  Max:     {latency_stats['max_ms']:.2f} ms")


def save_results(
    metrics: Dict[str, float],
    cm: Dict[str, int],
    latency_stats: Dict[str, Optional[float]],
    detailed_results: List[Dict],
    test_size: int,
    total_available: int,
    dataset_name: str
) -> Tuple[str, str]:
    """
    Save benchmark results to JSON files with timestamps.
    
    Args:
        metrics: Dictionary with accuracy, precision, recall, f1
        cm: Dictionary with confusion matrix values
        latency_stats: Dictionary with latency statistics
        detailed_results: List of detailed result dictionaries
        test_size: Number of samples tested
        total_available: Total samples available in dataset
        dataset_name: Name of the dataset used
        
    Returns:
        Tuple of (summary_file_path, detailed_file_path)
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare summary results (includes all records)
    summary_results = {
        "dataset_name": dataset_name,
        "confusion_matrix": cm,
        "metrics": metrics,
        "latency_stats": latency_stats,
        "total_samples": test_size,
        "total_available": total_available,
        "timestamp": datetime.now().isoformat(),
        "records": detailed_results  # Include all evaluated records
    }
    
    # Add dataset_name to each detailed result
    for result in detailed_results:
        result["dataset_name"] = dataset_name
    
    # Save summary results
    summary_file = f"benchmark_results_{timestamp_str}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary_results, f, indent=2)
    
    # Save detailed results
    detailed_file = f"benchmark_detailed_results_{timestamp_str}.json"
    with open(detailed_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    return summary_file, detailed_file


def run_benchmark(
    dataset_name: str,
    dataset_size: Optional[int] = None,
    dataset_adapter_name: Optional[str] = None
):
    """
    Run the benchmark against a dataset.
    
    Args:
        dataset_name: Name/path of the HuggingFace dataset
        dataset_size: Number of samples to test (None for all)
        dataset_adapter_name: Name of adapter to use (None for auto-detect)
    """
    # Load dataset
    print("\n📊 Loading dataset...")
    ds = load_dataset(dataset_name, token=HF_TOKEN)
    
    # Get the dataset (handle DatasetDict)
    # Prefer test split over train split if available
    if isinstance(ds, dict):
        splits = list(ds.keys())
        # Prefer 'test' split, then 'validation', then 'val', then any other split
        preferred_order = ['test', 'validation', 'val']
        selected_split = None
        
        for preferred in preferred_order:
            if preferred in splits:
                selected_split = preferred
                break
        
        if selected_split is None:
            # If no preferred split found, use the first available split
            selected_split = splits[0]
        
        dataset = ds[selected_split]
        print(f"✓ Using split: {selected_split} (available splits: {', '.join(splits)})")
    else:
        dataset = ds
    
    # Create dataset adapter for unified access
    if dataset_adapter_name:
        print(f"📌 Using adapter: {dataset_adapter_name}")
    else:
        print("🔍 Auto-detecting dataset format...")
    adapter = create_dataset_adapter(dataset, adapter_name=dataset_adapter_name)
    
    total_available = adapter.get_length()
    print(f"✓ Loaded {total_available} samples")
    
    # Determine how many samples to test
    test_size = dataset_size if dataset_size is not None else total_available
    test_size = min(test_size, total_available)
    print(f"📝 Testing {test_size} samples")
    
    
    # Run benchmark
    print("\n" + "=" * 80)
    print("Running benchmark through Enkrypt AI Guardrails...")
    print("=" * 80)
    
    y_true = []
    y_pred = []
    detailed_results = []
    
    # Process only the specified number of samples
    for i in tqdm(range(test_size), desc="Processing samples", unit="sample"):
        text = adapter.get_text(i)
        true_label, true_label_str = adapter.get_label(i)
        
        y_true.append(true_label)
        
        # Call guardrails API
        latency = None
        gr_label_str = "benign"
        predicted = 0
        error = None
        
        try:
            response, latency = call_guardrails_api(text)
            predicted = parse_for_attacks(response)
            gr_label_str = "jailbreak" if predicted else "benign"
            y_pred.append(1 if predicted else 0)
        except Exception as e:
            error = str(e)
            tqdm.write(f"⚠️  Error processing sample {i + 1}: {e}")
            # Default to benign (0) on error
            y_pred.append(0)
        
        # Store detailed results
        detailed_results.append({
            "text": text,
            "true_label": true_label_str,
            "gr_label": gr_label_str,
            "latency_ms": round(latency * 1000, 2) if latency is not None else None,
            "error": error
        })
    
    # Calculate metrics and statistics
    metrics = calculate_metrics(y_true, y_pred)
    cm = calculate_confusion_matrix_values(y_true, y_pred)
    latency_stats = calculate_latency_stats(detailed_results)
    
    # Display results
    display_results(metrics, cm, latency_stats)
    
    # Save results
    summary_file, detailed_file = save_results(
        metrics, cm, latency_stats, detailed_results, test_size, total_available, dataset_name
    )
    
    print(f"\n✓ Summary results saved to {summary_file}")
    print(f"✓ Detailed results saved to {detailed_file}")


def main():
    """Main benchmarking function - sets configuration variables."""
    print("=" * 80)
    print("ENKRYPT AI GUARDRAILS BENCHMARK")
    print("=" * 80)

    DATASET_SIZE = 100
    DATASET_NAME = "GuardrailsAI/detect-jailbreak"

    DATASET_ADAPTER_NAME = None 
    
    if not API_KEY:
        print("\n❌ Error: ENKRYPTAI_API_KEY not found in environment variables")
        print("   Please set ENKRYPTAI_API_KEY in your .env file")
        return
    
    if not HF_TOKEN:
        print("\n❌ Error: HF_TOKEN or HUGGINGFACE_TOKEN not found in environment variables")
        print("   Please set HF_TOKEN in your .env file")
        return
    
    run_benchmark(
        dataset_name=DATASET_NAME,
        dataset_size=DATASET_SIZE,
        dataset_adapter_name=DATASET_ADAPTER_NAME
    )


if __name__ == "__main__":
    main()