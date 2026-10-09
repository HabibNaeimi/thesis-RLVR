"""
Result comparison v1.0
"""

import json
from pathlib import Path

DATA_DIR = Path("data-collection/")
RESULTS_DIR = Path("comparison_results/")


def load_json(path: Path, default=None):
    if not path.is_file():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def comparison_results(
        case_id,
        ground_truth,
        submission,
        eval_metrics,
) -> dict:
    """
    Comparing every simulation results with the ground truth plus numerical
        evaluation results as results. 
        These results are not yet mapped to rewarding range.
    """
    
    # Primary reward contributers
    
    # Correct anomaly detection (A)
    correct_anolamy_detection = ground_truth['is_anomaly'] == submission['is_anomaly']
    # detection score
    detection_score = eval_metrics['detection_score']

    # Direct faulty resource metric on localization (L)
    localization_precision = eval_metrics['localization_precision']
    localization_recall = eval_metrics['localization_recall']
    localization_f1 = eval_metrics['localization_f1']

    predicted_root_causes = submission.get('root_causes', [])
    if predicted_root_causes:
        predicted_root_causes_resource_id = predicted_root_causes[0]['resource_id']
        predicted_root_causes_fault_type = predicted_root_causes[0]['fault_type']
    else:
        predicted_root_causes_fault_type = None
        predicted_root_causes_resource_id = None

    ground_truth_root_causes = ground_truth.get('root_causes', [])
    if ground_truth_root_causes:
        ground_truth_root_causes_resource_id = ground_truth_root_causes[0]['resource_id']
        ground_truth_root_causes_fault_type = ground_truth_root_causes[0]['fault_type']
    else:
        ground_truth_root_causes_resource_id = None
        ground_truth_root_causes_resource_id = None

    # checking resource_id on root caouse
    root_cause_resource_id_correctness = predicted_root_causes_resource_id == ground_truth_root_causes_resource_id
    

    # Secondary reward contributers
    
    # Fault type metrics
    fault_type_precision = eval_metrics['fault_type_precision']
    fault_type_recall = eval_metrics['fault_type_recall']
    fault_type_f1 = eval_metrics['fault_type_f1']

    # checking fault_type on root caouse
    root_cause_fault_type_correctness = predicted_root_causes_fault_type == ground_truth_root_causes_fault_type

    # correct fault_type on wrong resource = Faulty localization
    faulty_localization_correct_fault_type_wrong_resource = False
    if root_cause_fault_type_correctness:
        if not root_cause_resource_id_correctness:
            faulty_localization_correct_fault_type_wrong_resource = True

    # RCA metrics
    rca_precision = eval_metrics['rca_precision']
    rca_recall = eval_metrics['rca_recall']
    rca_f1 = eval_metrics['rca_f1']


    # Tertiary reward contributers

    in_tokens = eval_metrics['in_tokens']
    out_tokens = eval_metrics['out_tokens']
    steps = eval_metrics['steps']
    tool_calls = eval_metrics['tool_calls']
    tool_errors = eval_metrics['tool_errors']

    return {
        'case_id': case_id,
        'primary': {
            'correct_anolamy_detection': correct_anolamy_detection,
            'detection_score': detection_score,
            'localization_precision': localization_precision,
            'localization_recall': localization_recall,
            'localization_f1': localization_f1,
            'root_cause_resource_id_correctness': root_cause_resource_id_correctness,
        },
        'secondary': {
            'fault_type_precision': fault_type_precision,
            'fault_type_recall': fault_type_recall,
            'fault_type_f1': fault_type_f1,
            'root_cause_fault_type_correctness': root_cause_fault_type_correctness,
            'faulty_localization_correct_fault_type_wrong_resource': faulty_localization_correct_fault_type_wrong_resource,
            'rca_precision': rca_precision,
            'rca_recall': rca_recall,
            'rca_f1': rca_f1,
        },
        'tertiary': {
            'in_tokens': in_tokens,
            'out_tokens': out_tokens,
            'steps': steps,
            'tool_calls': tool_calls,
            'tool_errors': tool_errors,
        },
    }


def main():
    cases = (
        "dc_clos_s_host_missing_ip/20260929-165705-e487e1/",
        "dc_clos_s_link_down/20260929-165446-4c320f/"
    )
    for case_id in cases:
        case_dir = DATA_DIR / case_id
        case_results_dir = RESULTS_DIR / case_id

        ground_truth = load_json(case_dir / "ground_truth.json")
        submission   = load_json(case_dir / "submission.json")
        eval_metrics = load_json(case_dir / "eval_metrics.json")

        comparison_dict = comparison_results(
            case_id=case_id,
            ground_truth=ground_truth,
            submission=submission,
            eval_metrics=eval_metrics,
        )

        save_json(case_results_dir / "comparison_results.json", comparison_dict)

if __name__ == "__main__":
    main()
