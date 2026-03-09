# simulation.py
import time
import matplotlib.pyplot as plt

def measure_time(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    latency = (end - start) * 1000  # ms
    return result, latency


def generate_latency_graph(edge, fog, cloud):
    labels = ["Edge", "Fog", "Cloud"]
    values = [edge, fog, cloud]

    plt.figure()
    plt.bar(labels, values)
    plt.xlabel("Layer")
    plt.ylabel("Latency (ms)")
    plt.title("Edge-Fog-Cloud Latency")

    path = "latency.png"
    plt.savefig(path)
    plt.close()

    return path