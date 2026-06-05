# Pearl Mining Quick Start

## ⚡ 5-Minute Setup

### 1. Setup Cloudflare Tunnel (Local/VPS)

```bash
# Run automated setup
bash cloudflare-tunnel-setup.sh

# Or manual setup:
cloudflared tunnel login
cloudflared tunnel create pearl-mining
# Note the Tunnel ID from output
```

### 2. Configure Modal

```bash
# Install Modal
pip install modal

# Authenticate
modal token new

# Create wallet secret
modal secret create pearl-wallet PEARL_WALLET=prl1your-wallet-address-here
```

### 3. Update Configuration

Edit `modal_pearl.py` line 14:
```python
TUNNEL_HOST = "your-tunnel-id.cfargotunnel.com"  # From step 1
```

### 4. Deploy & Run

```bash
# Deploy app
modal deploy modal_pearl.py

# Test mining (1 hour on T4)
modal run modal_pearl.py::mine_short

# Full mining (2 hours on T4)
modal run modal_pearl.py
```

## 🎯 Quick Test Checklist

- [ ] Cloudflare tunnel running (`cloudflared tunnel run pearl-mining`)
- [ ] Tunnel hostname noted (`<id>.cfargotunnel.com`)
- [ ] Modal authenticated (`modal token new`)
- [ ] Wallet secret created
- [ ] `TUNNEL_HOST` updated in `modal_pearl.py`
- [ ] Test run completed successfully
- [ ] Earnings visible at https://pearlhash.xyz/?lookup=YOUR_WALLET

## 💡 Tips

**For Testing:**
- Start with `mine_short()` - 1 hour on T4 ($0.60)
- Check profitability before scaling
- Monitor first session closely

**For Production:**
- Use burst pattern (2-4 hours, then stop)
- Rotate worker names with timestamps
- Set billing alerts in Modal dashboard
- Don't run 24/7 (high ban risk)

**Cost Optimization:**
- T4 ($0.60/hr) - Good for testing
- L4 ($0.80/hr) - Better performance/price
- A100 ($3/hr) - High performance
- H100/H200 ($4.50-5.50/hr) - Maximum hashrate

## ⚠️ Important

- **ToS Risk**: Cloud mining may violate Modal ToS
- **Profitability**: Calculate ROI before scaling
- **Monitoring**: Check costs daily
- **Backup**: Save wallet credentials offline

## 🔗 Resources

- Pearl Dashboard: https://pearlhash.xyz
- Modal Dashboard: https://modal.com/apps
- Cloudflare Tunnel Docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
