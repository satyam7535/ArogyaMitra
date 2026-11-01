import time
import httpx
import statistics

def benchmark():
    url = "http://127.0.0.1:8000/predict"
    payload = {
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]
    }
    client = httpx.Client(timeout=10.0)
    
    # Warmup
    for _ in range(10):
        client.post(url, json=payload)
        
    latencies = []
    iterations = 200
    for _ in range(iterations):
        t0 = time.perf_counter()
        res = client.post(url, json=payload)
        t1 = time.perf_counter()
        if res.status_code != 200:
            raise RuntimeError(f"Error {res.status_code}: {res.text}")
        latencies.append((t1 - t0) * 1000.0) # in ms
        
    mean_val = statistics.mean(latencies)
    median_val = statistics.median(latencies)
    stdev_val = statistics.stdev(latencies)
    p95_val = sorted(latencies)[int(0.95 * len(latencies))]
    p99_val = sorted(latencies)[int(0.99 * len(latencies))]
    min_val = min(latencies)
    max_val = max(latencies)
    
    output = f"""================================================================================
AROGYAMITRA — ML INFERENCE LATENCY BENCHMARK
Endpoint: http://127.0.0.1:8000/predict
Model: Bernoulli Naive Bayes (41 Disease Classes, Exact Additive Log-Odds)
Iterations: {iterations}
Payload Symptoms: {payload['symptoms']}
================================================================================
Mean Latency:   {mean_val:.2f} ms
Median (p50):   {median_val:.2f} ms
p95 Latency:    {p95_val:.2f} ms
p99 Latency:    {p99_val:.2f} ms
Min Latency:    {min_val:.2f} ms
Max Latency:    {max_val:.2f} ms
Std Dev:        {stdev_val:.2f} ms
Status:         100% Successful (0 HTTP errors)
================================================================================
"""
    print(output)
    with open("docs/evidence/ml_inference_latency.txt", "w", encoding="utf-8") as f:
        f.write(output)
    print("Saved benchmark results to docs/evidence/ml_inference_latency.txt")

if __name__ == "__main__":
    benchmark()
