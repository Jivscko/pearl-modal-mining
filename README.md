# Pearl Mining on Modal.com via Cloudflare Tunnel

**⚠️ HIGH RISK**: Mining cryptocurrency on cloud providers typically violates Terms of Service. Use at your own risk. This is for educational purposes only.

[![GitHub](https://img.shields.io/badge/GitHub-pearl--modal--mining-blue?logo=github)](https://github.com/Jivscko/pearl-modal-mining)
[![Modal](https://img.shields.io/badge/Modal-GPU%20Mining-orange)](https://modal.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Quick Start (10 Minutes)

```bash
git clone https://github.com/Jivscko/pearl-modal-mining.git
cd pearl-modal-mining

# 1. Setup Cloudflare Tunnel (one-time)
bash cloudflare-tunnel-setup.sh

# 2. Install Modal
pip install modal
modal token new

# 3. Configure wallet
modal secret create pearl-wallet PEARL_WALLET=prl1your-wallet-here

# 4. Update tunnel hostname in modal_pearl.py (line 14)
# TUNNEL_HOST = "your-tunnel-id.cfargotunnel.com"

# 5. Deploy & run
modal deploy modal_pearl.py
modal run modal_pearl.py::mine_short  # 1-hour test on T4 ($0.60)
```

📖 **Detailed guide**: [QUICKSTART.md](QUICKSTART.md)

## 🏗️ Architecture

```
Modal GPU Container → Cloudflare Tunnel → Pearl Pool (84.32.220.219:9000)
```

**Why Cloudflare Tunnel?**
- Masks Modal IP from mining pool
- Masks pool IP from Modal detection systems
- Free tier, low latency (<50ms)
- Easy setup with automated script

## 📋 Requirements

### 1. Cloudflare Account (Free)
- Sign up at https://dash.cloudflare.com
- No domain needed (free `*.cfargotunnel.com` hostname)
- Takes 2 minutes to register

### 2. Cloudflared Binary (Local/VPS)

Install on Linux/WSL:
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

macOS:
```bash
brew install cloudflared
```

Windows:
```powershell
# Download from https://github.com/cloudflare/cloudflared/releases
# Or use WSL with Linux instructions above
```

### 3. Setup Tunnel (5 Minutes)

**Automated (recommended):**
```bash
cd pearl-modal-mining
bash cloudflare-tunnel-setup.sh
```

**Manual:**
```bash
# Login to Cloudflare (opens browser)
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create pearl-mining

# Output shows Tunnel ID, example:
# Created tunnel pearl-mining with id abc123...
# Credentials written to: ~/.cloudflared/abc123.json
# Tunnel hostname: abc123.cfargotunnel.com
```

### 4. Run Tunnel (Keep Alive)

**Foreground (testing):**
```bash
cloudflared tunnel --url tcp://84.32.220.219:9000
# Output: https://xxxx.trycloudflare.com (temporary)
```

**Background (persistent):**
```bash
# Create config
cat > ~/.cloudflared/config.yml << EOF
tunnel: abc123  # Your tunnel ID
credentials-file: /home/user/.cloudflared/abc123.json

ingress:
  - service: tcp://84.32.220.219:9000
EOF

# Run tunnel
cloudflared tunnel run pearl-mining

# Or install as systemd service (auto-start on boot)
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 5. Update Modal Config

Edit `modal_pearl.py` line 14:
```python
TUNNEL_HOST = "abc123.cfargotunnel.com"  # Replace with your tunnel ID
```

### 6. Verify Tunnel

Before mining, check tunnel is active:
```bash
# Terminal 1: Run tunnel
cloudflared tunnel run pearl-mining

# Terminal 2: Test connection
nc -zv abc123.cfargotunnel.com 9000
# Or
curl -v telnet://abc123.cfargotunnel.com:9000
```

If successful, you'll see "Connected" or similar output.

### 7. Where to Run Tunnel?

**Option A: Local Machine (Laptop/Desktop)**
- **Pros**: Free, full control
- **Cons**: Must stay online during mining
- **Best for**: Testing, short mining sessions

**Option B: Cheap VPS ($3-5/mo)**
- **Pros**: 24/7 uptime, reliable
- **Cons**: Additional cost
- **Providers**: Hetzner, DigitalOcean, Vultr, Linode
- **Best for**: Production mining

**Option C: Free Tier VPS**
- **Oracle Cloud (Always Free)**: 2 VMs free forever (ARM/x86)
- **Google Cloud (Free Tier)**: $300 credit for 90 days
- **Best for**: Testing without local machine dependency

## 💰 Cost & Profitability

| GPU | Modal Cost/hr | Hashrate | Break-even PRL/hr* |
|-----|---------------|----------|-------------------|
| T4 | $0.60 | Low | 0.6 PRL |
| L4 | $0.80 | Medium | 0.8 PRL |
| A100 | $3.00 | High | 3.0 PRL |
| H100 | $4.50 | Very High | 4.5 PRL |
| H200 | $5.50 | Maximum | 5.5 PRL |

*Assuming PRL = $1. Check current price before mining.

⚠️ **Test profitability first**: Run 1-hour test on T4, calculate ROI, then scale.

## 📁 Files

- **modal_pearl.py** - Modal serverless function (2-hour burst mining)
- **notebook_pearl.ipynb** - Jupyter notebook for interactive mining
- **cloudflare-tunnel-setup.sh** - Automated tunnel setup
- **QUICKSTART.md** - Step-by-step setup guide
- **.env.example** - Configuration template

## 🎓 Features

- ✅ Multiple GPU support (T4, L4, A100, H100, H200)
- ✅ Cloudflare Tunnel for IP masking
- ✅ Burst mining pattern (2-hour sessions, auto-stop)
- ✅ Modal Notebooks support (interactive)
- ✅ Automated setup scripts
- ✅ Worker name rotation (timestamp-based)
- ✅ Cost optimization guides

## 📊 Monitoring

```bash
# Check Modal logs
modal logs pearl-miner

# Verify tunnel status
cloudflared tunnel info pearl-mining

# Check earnings
# https://pearlhash.xyz/?lookup=YOUR_WALLET
```

## ⚠️ Risks & Disclaimers

1. **Terms of Service Violation**: Cloud mining typically violates Modal.com ToS
2. **Account Ban**: Modal may ban your account if detected
3. **Profitability**: GPU costs may exceed mining rewards
4. **No Guarantees**: Educational project, use at your own risk

## 🛡️ Risk Mitigation

- Don't run 24/7 (use burst pattern: 2-4 hours, then stop)
- Rotate worker names with timestamps
- Monitor costs daily (set billing alerts)
- Test on T4 first before expensive GPUs
- Have backup plan (export wallet, save credentials)

## 🔄 Safer Alternatives

- **RunPod**: Mining-friendly, $0.30-0.80/hr
- **Vast.ai**: Peer-to-peer GPU rental, cheaper
- **Akash Network**: Decentralized, crypto-native
- **Hetzner**: Dedicated GPU servers, €60-150/mo

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for improvement ideas:
- Profitability dashboard
- Auto-rotation & scheduling
- Telegram/Discord alerts
- Alternative cloud providers

## 📄 License

MIT - See [LICENSE](LICENSE)

**DISCLAIMER**: Mining cryptocurrency on cloud computing platforms may violate their Terms of Service. Users assume all risks and responsibilities for compliance with applicable terms and laws. This software is provided for educational purposes only.

---

🔗 **Links**
- Pearl Dashboard: https://pearlhash.xyz
- Modal Dashboard: https://modal.com/apps
- Cloudflare Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

**Support**: Open an issue or PR if you find bugs or have improvements.
