import json
import os
import pandas as pd
from analyzer import analyze


def confidence_bucket(confidence: int) -> str:
    if confidence >= 90:
        return "High (90-100)"
    elif confidence >= 70:
        return "Medium (70-89)"
    else:
        return "Low (<70)"


def main():
    failures_path = os.path.join(os.path.dirname(__file__), "failures.json")
    with open(failures_path, "r", encoding="utf-8") as f:
        failures = json.load(f)

    rows = []
    for i, entry in enumerate(failures, start=1):
        print(f"Analyzing [{i}/10]: {entry['name']}...")
        result = analyze(entry["raw_log"])

        is_correct = (
            result.severity == entry["correct_severity"]
            and result.auto_recoverable == entry["auto_recoverable"]
        )

        rows.append({
            "id": entry["id"],
            "name": entry["name"],
            "correct_severity": entry["correct_severity"],
            "model_severity": result.severity,
            "correct_auto_recoverable": entry["auto_recoverable"],
            "model_auto_recoverable": result.auto_recoverable,
            "confidence": result.confidence,
            "escalated": result.escalate,
            "is_correct": is_correct,
            "confidence_bucket": confidence_bucket(result.confidence),
        })

    df = pd.DataFrame(rows)

    output_path = os.path.join(os.path.dirname(__file__), "eval_results.csv")
    df.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}\n")

    # Build summary table per bucket
    bucket_order = ["High (90-100)", "Medium (70-89)", "Low (<70)"]
    summary_rows = []

    for bucket in bucket_order:
        subset = df[df["confidence_bucket"] == bucket]
        if len(subset) == 0:
            continue
        accuracy = subset["is_correct"].mean() * 100
        escalated_pct = subset["escalated"].mean() * 100
        summary_rows.append({
            "Confidence Bucket": bucket,
            "Accuracy": f"{accuracy:.0f}%",
            "Escalated": f"{escalated_pct:.0f}%",
            "Count": len(subset),
        })

    # Overall row
    summary_rows.append({
        "Confidence Bucket": "OVERALL",
        "Accuracy": f"{df['is_correct'].mean() * 100:.0f}%",
        "Escalated": f"{df['escalated'].mean() * 100:.0f}%",
        "Count": len(df),
    })

    summary = pd.DataFrame(summary_rows)

    # Print formatted table
    col_widths = {
        "Confidence Bucket": 18,
        "Accuracy": 10,
        "Escalated": 11,
        "Count": 7,
    }
    header = (
        f"{'Confidence Bucket':<18} | "
        f"{'Accuracy':>8} | "
        f"{'Escalated':>9} | "
        f"{'Count':>5}"
    )
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)
    for _, row in summary.iterrows():
        print(
            f"{row['Confidence Bucket']:<18} | "
            f"{row['Accuracy']:>8} | "
            f"{row['Escalated']:>9} | "
            f"{row['Count']:>5}"
        )
    print(separator)

    # KEY FINDING
    high_rows = df[df["confidence_bucket"] == "High (90-100)"]
    medium_rows = df[df["confidence_bucket"] == "Medium (70-89)"]

    print()
    if len(high_rows) == 0:
        print("KEY FINDING: Insufficient high-confidence results to assess calibration")
    else:
        high_acc = high_rows["is_correct"].mean()
        if len(medium_rows) == 0 or high_acc > medium_rows["is_correct"].mean():
            print(
                "KEY FINDING: Model is well-calibrated — high confidence correlates with accuracy"
            )
        else:
            print(
                "KEY FINDING: Model shows overconfidence — high confidence does NOT reliably "
                "predict accuracy (same pattern found in bookkeeping eval)"
            )


if __name__ == "__main__":
    main()
