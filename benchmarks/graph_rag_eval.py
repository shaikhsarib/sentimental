import argparse
import json
import urllib.parse
import urllib.request


def fetch_rag(api_base: str, project_id: str, query: str) -> dict:
    params = urllib.parse.urlencode({"query": query})
    url = f"{api_base}/api/v6/projects/{project_id}/rag?{params}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def keyword_hit(text: str, keywords) -> float:
    if not text:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for k in keywords if k.lower() in text_lower)
    return hits / max(1, len(keywords))


def main():
    parser = argparse.ArgumentParser(description="Evaluate GraphRAG keyword coverage.")
    parser.add_argument("--api", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--project_id", required=True, help="V6 project id")
    parser.add_argument("--dataset", required=True, help="JSON file with queries and expected keywords")
    args = parser.parse_args()

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    if total == 0:
        print("No evaluation items found.")
        return

    scores = []
    for item in dataset:
        query = item.get("query", "")
        keywords = item.get("expected_keywords", [])
        rag = fetch_rag(args.api, args.project_id, query)
        answer = (rag.get("summary") or {}).get("answer", "")
        score = keyword_hit(answer, keywords)
        scores.append(score)
        print(f"Query: {query}\nScore: {score:.2f}\n")

    avg = sum(scores) / len(scores)
    print(f"Average keyword coverage: {avg:.2f} ({len(scores)} queries)")


if __name__ == "__main__":
    main()
