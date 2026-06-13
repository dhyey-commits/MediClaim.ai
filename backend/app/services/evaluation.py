import re

def normalize_text(text: str) -> str:
    """Normalize text by lowercasing, stripping, and removing punctuation."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())

def calculate_scalar_accuracy(gt: str, sys_out: str) -> float:
    """Calculate accuracy for scalar strings (1.0 if match, 0.0 if mismatch)."""
    return 1.0 if normalize_text(gt) == normalize_text(sys_out) else 0.0

def calculate_list_metrics(gt_list: list[str], sys_out_list: list[str]) -> dict:
    """Calculate Precision, Recall, and Accuracy for lists of strings."""
    gt_norm = set(normalize_text(x) for x in gt_list if x)
    sys_norm = set(normalize_text(x) for x in sys_out_list if x)

    tp = len(gt_norm.intersection(sys_norm))
    fp = len(sys_norm - gt_norm)
    fn = len(gt_norm - sys_norm)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # Strict list accuracy could be defined as exact set match, but F1 is better
    accuracy = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "accuracy": round(accuracy, 2),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }

def evaluate_claim(ground_truth: dict, system_output: dict) -> dict:
    """
    Evaluates a single claim against ground truth.
    Returns metrics dict.
    """
    metrics = {
        "scalar_fields": {},
        "list_fields": {},
        "overall": {}
    }

    # Evaluate Scalar Fields
    scalar_keys = ["patient_name", "age", "gender", "admission_date", "discharge_date"]
    scalar_acc = []
    for k in scalar_keys:
        acc = calculate_scalar_accuracy(ground_truth.get(k, ""), system_output.get(k, ""))
        metrics["scalar_fields"][k] = {"accuracy": acc}
        scalar_acc.append(acc)

    # Evaluate List Fields
    list_keys = ["diagnoses", "procedures", "medications", "investigations", "icd_recommendations"]
    list_precisions, list_recalls, list_accs = [], [], []
    for k in list_keys:
        res = calculate_list_metrics(ground_truth.get(k, []), system_output.get(k, []))
        metrics["list_fields"][k] = res
        list_precisions.append(res["precision"])
        list_recalls.append(res["recall"])
        list_accs.append(res["accuracy"])

    # Aggregate Overall Metrics
    overall_acc = (sum(scalar_acc) + sum(list_accs)) / (len(scalar_acc) + len(list_accs)) if (len(scalar_acc) + len(list_accs)) > 0 else 0.0
    overall_prec = sum(list_precisions) / len(list_precisions) if len(list_precisions) > 0 else 0.0
    overall_rec = sum(list_recalls) / len(list_recalls) if len(list_recalls) > 0 else 0.0

    metrics["overall"] = {
        "accuracy": round(overall_acc, 2),
        "precision": round(overall_prec, 2),
        "recall": round(overall_rec, 2)
    }

    return metrics
