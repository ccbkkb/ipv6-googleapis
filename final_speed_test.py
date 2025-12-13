import socket
import time
import sys
import statistics
import os

FILES_TO_CHECK = ["valid_ips.txt"]
TARGET_PORT = 443
TIMEOUT = 2

def get_region(ip):
    if ip.startswith("2404:6800"): return "Asia"
    if ip.startswith("2607:f8b0"): return "US"
    if ip.startswith("2a00:1450"): return "EU"
    return "Unknown"

def tcp_ping(ip):
    times = []
    for _ in range(3):
        try:
            start = time.time()
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.settimeout(TIMEOUT)
            s.connect((ip, TARGET_PORT))
            s.close()
            times.append((time.time() - start) * 1000)
        except:
            return float('inf')
    return statistics.mean(times)

def main():
    ips = set()
    for filename in FILES_TO_CHECK:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line: ips.add(line)
            
    if not ips:
        print("No IPs found.")
        return

    print(f"Testing {len(ips)} IPs...")
    
    results = []
    for ip in ips:
        latency = tcp_ping(ip)
        region = get_region(ip)
        
        if latency != float('inf'):
            print(f"{ip:<35} | {region:<5} | {latency:.1f} ms")
            results.append((ip, latency, region))

    results.sort(key=lambda x: x[1])

    print("\nTOP 5 IPs:")
    for i, (ip, lat, reg) in enumerate(results[:5]):
        print(f"{i+1}. {ip} ({reg}) -> {lat:.1f} ms")
    
    if results:
        best_ip = results[0][0]
        print(f"\nBest Host: {best_ip} generativelanguage.googleapis.com")

if __name__ == "__main__":
    main()
