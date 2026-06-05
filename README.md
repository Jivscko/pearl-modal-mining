# Pearl Mining on Modal.com via Cloudflare Tunnel

**⚠️ HIGH RISK**: Mining cryptocurrency on cloud providers typically violates Terms of Service. Use at your own risk.

## Architecture

```
Modal GPU Container → Cloudflare Tunnel → Pearl Mining Pool (84.32.220.219:9000)
```

**Why Cloudflare Tunnel:**
- Masks Modal IP from mining pool
- Masks pool IP from Modal (reduces detection)
- Low latency (<50ms overhead)
- Free tier sufficient for mining traffic

## Setup

### 1. Cloudflare Tunnel Setup (Local/VPS)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create pearl-mining

# Note the Tunnel ID and credentials file path
# Credentials saved to: ~/.cloudflared/<TUNNEL-ID>.json
```

### 2. Configure Tunnel

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /home/user/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: pearl.yourdomain.com  # Optional: use a domain
    service: tcp://84.32.220.219:9000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tcpKeepAlive: 30s
  - service: http_status:404  # Catch-all rule
```

**Or for quick start without domain:**

```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /home/user/.cloudflared/<TUNNEL-ID>.json

ingress:
  - service: tcp://84.32.220.219:9000
```

### 3. Run Tunnel (Persistent)

```bash
# Test first
cloudflared tunnel run pearl-mining

# Run as systemd service (recommended)
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

**Get your tunnel endpoint:**
```bash
cloudflared tunnel info pearl-mining
# Note the public hostname: <tunnel-id>.cfargotunnel.com
```

### 4. Modal Setup

```bash
# Install Modal
pip install modal

# Authenticate
modal token new

# Set your wallet as secret
modal secret create pearl-wallet PEARL_WALLET=prl1your-wallet-address-here

# Deploy
modal deploy modal_pearl.py
```

### 5. Run Mining

**Option A: Serverless Function (auto-scale)**
```bash
modal run modal_pearl.py
```

**Option B: Notebook (interactive)**
- Open https://modal.com/notebooks
- Upload `notebook_pearl.ipynb`
- Select GPU (T4 for testing, H100/H200 for performance)
- Run cells

## Configuration

Edit `modal_pearl.py`:

```python
TUNNEL_HOST = "<tunnel-id>.cfargotunnel.com"  # From step 3
TUNNEL_PORT = "9000"  # Default Cloudflare tunnel port
PEARL_WALLET = "prl1your-wallet-here"  # Or use modal secret
WORKER_NAME = "modal-miner-1"  # Unique worker ID
```

## Cost Estimation

**Modal GPU Pricing (approximate):**
- T4: $0.60/hr
- L4: $0.80/hr
- A100-40GB: $3.00/hr
- H100: $4.50/hr
- H200: $5.50/hr

**Profitability depends on:**
- PRL token price
- Network difficulty
- Epoch rewards
- GPU hashrate

⚠️ **Test with T4 first (cheapest) to verify profitability before scaling to expensive GPUs.**

## Monitoring

```bash
# Check Modal logs
modal logs <app-name>

# Check tunnel traffic
cloudflared tunnel info pearl-mining

# Verify earnings
# Visit: https://pearlhash.xyz/?lookup=YOUR_WALLET
```

## Risk Mitigation

1. **Don't run 24/7** - Burst mining pattern (2-4 hrs/session)
2. **Rotate worker names** - Use timestamp in worker ID
3. **Monitor costs** - Set billing alerts in Modal dashboard
4. **Test profitability** - Run 1 hour on T4, calculate ROI
5. **Have backup plan** - Export wallet, save credentials

## Safer Alternatives

- **RunPod**: Mining-friendly, $0.30-0.80/hr for RTX 4090
- **Vast.ai**: Peer-to-peer GPU rental, cheap but unreliable
- **Akash Network**: Decentralized, crypto-native
- **Hetzner dedicated**: €60-150/mo for dedicated GPU servers

## Files

- `modal_pearl.py` - Modal serverless function
- `notebook_pearl.ipynb` - Jupyter notebook for interactive mining
- `Dockerfile` - Container image (nvidia/cuda base)
- `mine.sh` - Mining startup script
- `.env.example` - Environment variables template

## License

MIT - Use at your own risk. Mining crypto on cloud providers may violate ToS.
