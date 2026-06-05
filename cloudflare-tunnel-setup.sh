#!/bin/bash
set -e

echo "🔷 Cloudflare Tunnel Setup for Pearl Mining"
echo "=============================================="
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installing cloudflared..."
    
    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        BINARY="cloudflared-linux-amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        BINARY="cloudflared-linux-arm64"
    else
        echo "❌ Unsupported architecture: $ARCH"
        exit 1
    fi
    
    wget -q "https://github.com/cloudflare/cloudflared/releases/latest/download/$BINARY" -O cloudflared
    chmod +x cloudflared
    sudo mv cloudflared /usr/local/bin/cloudflared
    
    echo "✅ cloudflared installed"
else
    echo "✅ cloudflared already installed"
fi

cloudflared --version
echo ""

# Login to Cloudflare
echo "🔐 Cloudflare Authentication"
echo "   This will open a browser to authenticate."
echo "   Press Enter to continue..."
read

cloudflared tunnel login

echo ""
echo "✅ Authenticated with Cloudflare"
echo ""

# Create tunnel
TUNNEL_NAME="pearl-mining-$(date +%s)"
echo "🔧 Creating tunnel: $TUNNEL_NAME"

cloudflared tunnel create "$TUNNEL_NAME"

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Failed to create tunnel"
    exit 1
fi

echo "✅ Tunnel created: $TUNNEL_ID"
echo ""

# Create config
CONFIG_DIR="$HOME/.cloudflared"
mkdir -p "$CONFIG_DIR"

CONFIG_FILE="$CONFIG_DIR/config.yml"

cat > "$CONFIG_FILE" <<EOF
tunnel: $TUNNEL_ID
credentials-file: $CONFIG_DIR/$TUNNEL_ID.json

ingress:
  - service: tcp://84.32.220.219:9000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tcpKeepAlive: 30s
EOF

echo "✅ Config created: $CONFIG_FILE"
echo ""

# Get tunnel info
echo "📊 Tunnel Information"
cloudflared tunnel info "$TUNNEL_NAME"
echo ""

# Show tunnel hostname
TUNNEL_HOSTNAME="$TUNNEL_ID.cfargotunnel.com"

echo "=============================================="
echo "✅ Setup Complete!"
echo ""
echo "🔑 Tunnel Details:"
echo "   ID: $TUNNEL_ID"
echo "   Name: $TUNNEL_NAME"
echo "   Hostname: $TUNNEL_HOSTNAME"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Test tunnel:"
echo "   cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "2. Install as service (persistent):"
echo "   sudo cloudflared service install"
echo "   sudo systemctl start cloudflared"
echo "   sudo systemctl enable cloudflared"
echo ""
echo "3. Update Modal configuration:"
echo "   TUNNEL_HOST=$TUNNEL_HOSTNAME"
echo ""
echo "4. Create Modal secret:"
echo "   modal secret create pearl-wallet PEARL_WALLET=prl1your-wallet-here"
echo ""
echo "5. Deploy to Modal:"
echo "   modal deploy modal_pearl.py"
echo ""
echo "=============================================="
