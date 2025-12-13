import socket
import ssl
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor

TARGET_HOST = "generativelanguage.googleapis.com"
TARGET_PORT = 443
OUTPUT_FILE = "valid_ips.txt"
MAX_THREADS = 400
TIMEOUT = 1.5

REGIONS = [
    "2607:f8b0",
    "2404:6800",
    "2a00:1450",
]

L3_RANGE = range(0x4000, 0x4011)
L4_RANGE = range(0x800, 0x821)
SUFFIXES = ["200a", "200e"]

valid_ips = set()
lock = threading.Lock()

def check_ip(ip):
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        
        ssl_sock = context.wrap_socket(sock, server_hostname=TARGET_HOST)
        ssl_sock.connect((ip, TARGET_PORT))
        ssl_sock.close()
        sock.close()
        
        with lock:
            print(f"[SUCCESS] {ip}")
            valid_ips.add(ip)
    except:
        pass

def generate_targets():
    targets = []
    print(f"[*] Generating target matrix...")
    for region in REGIONS:
        for l3 in L3_RANGE:
            l3_hex = hex(l3)[2:]
            for l4 in L4_RANGE:
                l4_hex = hex(l4)[2:]
                for suffix in SUFFIXES:
                    ip = f"{region}:{l3_hex}:{l4_hex}::{suffix}"
                    targets.append(ip)
    return targets

def save_results():
    # 'w' mode ensures the file is overwritten (truncated) every time
    with open(OUTPUT_FILE, 'w') as f:
        sorted_ips = sorted(list(valid_ips), key=lambda x: (
            0 if x.startswith("2404") else 
            1 if x.startswith("2607") else 2
        ))
        for ip in sorted_ips:
            f.write(f"{ip}\n")

def main():
    # Removed load_existing() to ensure we only keep currently valid IPs
    
    if not socket.has_ipv6:
        print("[!] Warning: System claims no IPv6, but we will try anyway (WARP mode).")

    targets = generate_targets()
    print(f"[*] Scanning {len(targets)} targets with {MAX_THREADS} threads...")
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(check_ip, targets)
        
    print(f"[*] Scan complete. Total valid: {len(valid_ips)}")
    save_results()

if __name__ == "__main__":
    main()
