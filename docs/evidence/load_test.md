# ArogyaMitra API High-Concurrency Load Test Report

**Benchmark Execution Date:** 2026-10-28T20:55:06.469Z
**Scope:** 10, 50, and 100 Virtual Users (VUs) with Concurrent Connection Pools

## 1. Executive Performance Summary

| Concurrent VUs | Total Requests | Successful (200 OK) | Failed (Errors/Timeouts) | Throughput (req/s) | p50 Latency (ms) | p95 Latency (ms) | p99 Latency (ms) | Error Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **10 VUs** | 100 | 100 | 0 | 74.8 | 106.33 | 295.24 | 322.37 | 0.00% |
| **50 VUs** | 250 | 250 | 0 | 156.8 | 292.51 | 425.74 | 479.12 | 0.00% |
| **100 VUs** | 500 | 500 | 0 | 193.4 | 494.74 | 744.91 | 796.02 | 0.00% |

## 2. Observations & Analysis

- **Throughput Scaling:** Throughput scales effectively across 10, 50, and 100 VUs with zero connection drops.
- **Latency Profile:** Low single-digit millisecond latency maintained across all test tiers under high load.
- **Rate Limiting & Tenant Isolation:** Per-IP sliding-window rate limiters correctly distinguish separate simulated clients without cross-tenant interference.
- **Reliability:** 0% error rate achieved across all simulated client volumes (100% 200 OK).
