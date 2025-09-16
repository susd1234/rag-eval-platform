"""
Example usage of the SME Evaluation Platform API with selective metrics processing
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:9777"


def test_single_metric_evaluation():
    """Test evaluation with only Accuracy metric"""

    url = f"{BASE_URL}/evaluation/evaluate"

    payload = {
        "eval_metrices": ["Accuracy"],
        "user_query": "What is the capital of France?",
        "ai_response": "The capital of France is Paris. Paris is located in the north-central part of France and serves as the country's political, economic, and cultural center.",
        "chunk_1": "France Geography: Paris is the capital and largest city of France, located in the north-central part of the country.",
        "chunk_2": "",
        "chunk_3": "",
        "chunk_4": "",
        "chunk_5": "",
    }

    response = requests.post(url, json=payload)
    print("=== Single Metric (Accuracy) Evaluation ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n")


def test_two_metrics_evaluation():
    """Test evaluation with Accuracy and Usefulness metrics"""

    url = f"{BASE_URL}/evaluation/evaluate"

    payload = {
        "eval_metrices": ["Accuracy", "Usefulness"],
        "user_query": "Is a verbal employment contract enforceable in California?",
        "ai_response": "Yes, verbal employment contracts are generally enforceable in California under specific circumstances, though written contracts provide stronger legal protection.",
        "chunk_1": "California Employment Contract Law: Labor Code Section 2922 - California At-Will Employment",
        "chunk_2": "Verbal Contract Enforceability Standards: Foley v. Interactive Data Corp., 47 Cal. 3d 654 (1988)",
        "chunk_3": "",
        "chunk_4": "",
        "chunk_5": "",
    }

    response = requests.post(url, json=payload)
    print("=== Two Metrics (Accuracy + Usefulness) Evaluation ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n")


def test_all_metrics_evaluation():
    """Test evaluation with all metrics (default behavior)"""

    url = f"{BASE_URL}/evaluation/evaluate"

    payload = {
        "eval_metrices": [
            "Accuracy",
            "Hallucination",
            "Authoritativeness",
            "Usefulness",
        ],
        "user_query": "Explain the difference between criminal and civil law.",
        "ai_response": "Criminal law deals with offenses against the state, while civil law governs disputes between private parties. Criminal cases are prosecuted by the government and can result in imprisonment, while civil cases seek monetary damages or equitable relief.",
        "chunk_1": "Criminal Law Fundamentals: Criminal law encompasses offenses against society as represented by the government.",
        "chunk_2": "Civil Law Overview: Civil law governs relationships between individuals and organizations.",
        "chunk_3": "Legal System Distinctions: The burden of proof differs between criminal (beyond reasonable doubt) and civil (preponderance of evidence) cases.",
        "chunk_4": "",
        "chunk_5": "",
    }

    response = requests.post(url, json=payload)
    print("=== All Metrics Evaluation ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n")


def test_invalid_metrics():
    """Test evaluation with invalid metrics to show validation"""

    url = f"{BASE_URL}/evaluation/evaluate"

    payload = {
        "eval_metrices": ["Accuracy", "InvalidMetric"],
        "user_query": "Test query",
        "ai_response": "Test response",
        "chunk_1": "",
        "chunk_2": "",
        "chunk_3": "",
        "chunk_4": "",
        "chunk_5": "",
    }

    response = requests.post(url, json=payload)
    print("=== Invalid Metrics Test (Should Fail) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n")


def test_empty_metrics():
    """Test evaluation with empty metrics list to show validation"""

    url = f"{BASE_URL}/evaluation/evaluate"

    payload = {
        "eval_metrices": [],
        "user_query": "Test query",
        "ai_response": "Test response",
        "chunk_1": "",
        "chunk_2": "",
        "chunk_3": "",
        "chunk_4": "",
        "chunk_5": "",
    }

    response = requests.post(url, json=payload)
    print("=== Empty Metrics Test (Should Fail) ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n")


def test_predefined_endpoints():
    """Test the predefined test endpoints"""

    # Test the default test endpoint (Accuracy + Usefulness)
    response = requests.post(f"{BASE_URL}/evaluation/test")
    print("=== Predefined Test Endpoint (Accuracy + Usefulness) ===")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Evaluation ID: {result['evaluation_id']}")
        print(f"Processing Time: {result['processing_time']}s")
        print(f"Overall Rating: {result['overall']['overall_rating']}")
        print(f"Accuracy: {'Present' if result['accuracy'] else 'Null'}")
        print(f"Hallucination: {'Present' if result['hallucination'] else 'Null'}")
        print(
            f"Authoritativeness: {'Present' if result['authoritativeness'] else 'Null'}"
        )
        print(f"Usefulness: {'Present' if result['usefulness'] else 'Null'}")
    print("\n")

    # Test the single metric endpoint
    response = requests.post(f"{BASE_URL}/evaluation/test/single-metric")
    print("=== Predefined Single Metric Test Endpoint (Accuracy Only) ===")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Evaluation ID: {result['evaluation_id']}")
        print(f"Processing Time: {result['processing_time']}s")
        print(f"Overall Rating: {result['overall']['overall_rating']}")
        print(f"Accuracy: {'Present' if result['accuracy'] else 'Null'}")
        print(f"Hallucination: {'Present' if result['hallucination'] else 'Null'}")
        print(
            f"Authoritativeness: {'Present' if result['authoritativeness'] else 'Null'}"
        )
        print(f"Usefulness: {'Present' if result['usefulness'] else 'Null'}")
    print("\n")


def test_system_health():
    """Test system health endpoint"""

    response = requests.get(f"{BASE_URL}/evaluation/system/health")
    print("=== System Health Check ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("\n")


def main():
    """Run all test examples"""
    print("SME Evaluation Platform - Selective Metrics API Testing")
    print("=" * 60)

    try:
        # Test system health first
        test_system_health()

        # Test selective metric processing
        test_single_metric_evaluation()
        test_two_metrics_evaluation()
        test_all_metrics_evaluation()

        # Test validation
        test_invalid_metrics()
        test_empty_metrics()

        # Test predefined endpoints
        test_predefined_endpoints()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:9777")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
