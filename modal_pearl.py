"""
Pearl (PRL) Mining on Modal.com via Cloudflare Tunnel

WARNING: Mining cryptocurrency on cloud providers may violate Terms of Service.
Use at your own risk. This is for educational purposes only.
"""

import modal
import os
from datetime import datetime

# Configuration
TUNNEL_HOST = os.environ.get("TUNNEL_HOST", "your-tunnel-id.cfargotunnel.com")
TUNNEL_PORT = os.environ.get("TUNNEL_PORT", "9000")
MINER_URL = "https://pearlhash.xyz/downloads/pearl-miner-v4"

# Worker name with timestamp to avoid conflicts
WORKER_NAME = f"modal-{datetime.utcnow().strftime('%Y%m%d-%H%M')}"

# Container image based on nvidia/cuda
image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.4.1-runtime-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install("curl", "ca-certificates", "libgomp1")
    .run_commands(
        f"curl -fsSL -o /usr/local/bin/pearl-miner {MINER_URL}",
        "chmod +x /usr/local/bin/pearl-miner",
    )
)

app = modal.App("pearl-miner", image=image)


@app.function(
    gpu="T4",  # Start with cheapest GPU for testing
    timeout=7200,  # 2 hour max runtime
    secrets=[modal.Secret.from_name("pearl-wallet")],  # PEARL_WALLET env var
)
def mine():
    """
    Run Pearl miner for 2 hours then exit (burst mining pattern).
    
    To use more powerful GPU, change gpu parameter:
    - gpu="L4"        # ~$0.80/hr
    - gpu="A100"      # ~$3.00/hr
    - gpu="H100"      # ~$4.50/hr
    - gpu="H200"      # ~$5.50/hr
    """
    import subprocess
    import time
    
    wallet = os.environ.get("PEARL_WALLET")
    if not wallet:
        raise ValueError("PEARL_WALLET secret not set. Run: modal secret create pearl-wallet PEARL_WALLET=prl1...")
    
    pool_host = f"{TUNNEL_HOST}:{TUNNEL_PORT}"
    
    print(f"🔷 Pearl Miner Starting")
    print(f"   Wallet: {wallet[:15]}...{wallet[-10:]}")
    print(f"   Worker: {WORKER_NAME}")
    print(f"   Pool: {pool_host} (via Cloudflare Tunnel)")
    print(f"   GPU: {os.environ.get('MODAL_GPU_TYPE', 'unknown')}")
    print(f"   Max runtime: 2 hours")
    print("=" * 60)
    
    # Run miner
    cmd = [
        "/usr/local/bin/pearl-miner",
        "--host", pool_host,
        "--user", wallet,
        "--worker", WORKER_NAME,
    ]
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        
        # Stream output
        for line in process.stdout:
            print(line.rstrip())
            
            # Check timeout (Modal function timeout is backup)
            if time.time() - start_time > 7000:  # 1h 56m
                print("⏱️  Approaching 2-hour limit, stopping gracefully...")
                process.terminate()
                process.wait(timeout=30)
                break
        
        process.wait()
        
    except KeyboardInterrupt:
        print("🛑 Interrupted, stopping miner...")
        process.terminate()
        process.wait(timeout=30)
    
    runtime = time.time() - start_time
    print("=" * 60)
    print(f"✅ Mining session completed")
    print(f"   Runtime: {runtime/60:.1f} minutes")
    print(f"   Check earnings: https://pearlhash.xyz/?lookup={wallet}")


@app.function(
    gpu="T4",
    timeout=3600,  # 1 hour
    secrets=[modal.Secret.from_name("pearl-wallet")],
)
def mine_short():
    """
    Shorter 1-hour mining session for testing profitability.
    """
    import subprocess
    import time
    
    wallet = os.environ.get("PEARL_WALLET")
    if not wallet:
        raise ValueError("PEARL_WALLET secret not set.")
    
    pool_host = f"{TUNNEL_HOST}:{TUNNEL_PORT}"
    
    print(f"🧪 Test Mining Session (1 hour)")
    print(f"   Wallet: {wallet[:15]}...{wallet[-10:]}")
    print(f"   Pool: {pool_host}")
    
    cmd = [
        "/usr/local/bin/pearl-miner",
        "--host", pool_host,
        "--user", wallet,
        "--worker", f"{WORKER_NAME}-test",
    ]
    
    start = time.time()
    subprocess.run(cmd, timeout=3500)  # 58 minutes max
    
    runtime = time.time() - start
    print(f"✅ Test completed: {runtime/60:.1f} minutes")
    print(f"   Calculate ROI before scaling to expensive GPUs")


@app.local_entrypoint()
def main():
    """
    Run mining session.
    
    Usage:
        modal run modal_pearl.py              # 2-hour session on T4
        modal run modal_pearl.py::mine_short  # 1-hour test session
    """
    print("🚀 Starting Pearl mining on Modal...")
    print(f"   Tunnel: {TUNNEL_HOST}:{TUNNEL_PORT}")
    print(f"   Worker: {WORKER_NAME}")
    print()
    
    mine.remote()
