#!/bin/bash
# ================================================
# GramAI - WiFi Hotspot Setup for Raspberry Pi
# Creates a local WiFi access point so nearby
# devices can connect and use GramAI
# ================================================
# Usage: sudo ./hotspot-setup.sh
# ================================================

set -e

echo "=============================================="
echo "📡 GramAI - WiFi Hotspot Setup"
echo "=============================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Please run as root (sudo ./hotspot-setup.sh)"
    exit 1
fi

# Configuration
SSID="GramAI-WiFi"
PASSWORD="gramai1234"
INTERFACE="wlan0"
IP_ADDRESS="192.168.4.1"
DHCP_RANGE_START="192.168.4.10"
DHCP_RANGE_END="192.168.4.100"

echo -e "${GREEN}WiFi Name (SSID): $SSID${NC}"
echo -e "${GREEN}Password: $PASSWORD${NC}"
echo -e "${GREEN}Server IP: $IP_ADDRESS${NC}"

# ---- Install Dependencies ----
echo -e "\n${GREEN}[1/4] Installing hostapd and dnsmasq...${NC}"
apt-get update -y
apt-get install -y hostapd dnsmasq

systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

# ---- Configure Static IP ----
echo -e "\n${GREEN}[2/4] Configuring static IP...${NC}"
cat >> /etc/dhcpcd.conf << EOF

# GramAI Hotspot Configuration
interface $INTERFACE
    static ip_address=$IP_ADDRESS/24
    nohook wpa_supplicant
EOF

# ---- Configure DHCP Server ----
echo -e "\n${GREEN}[3/4] Configuring DHCP...${NC}"
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak 2>/dev/null || true
cat > /etc/dnsmasq.conf << EOF
# GramAI DHCP Configuration
interface=$INTERFACE
dhcp-range=$DHCP_RANGE_START,$DHCP_RANGE_END,255.255.255.0,24h
# Redirect all DNS to this device
address=/#/$IP_ADDRESS
EOF

# ---- Configure Hostapd ----
echo -e "\n${GREEN}[4/4] Configuring WiFi Access Point...${NC}"
cat > /etc/hostapd/hostapd.conf << EOF
# GramAI WiFi Access Point
interface=$INTERFACE
driver=nl80211
ssid=$SSID
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Set hostapd config file
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Enable services
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

# Start services
systemctl start hostapd
systemctl start dnsmasq

echo -e "\n${GREEN}=============================================="
echo "✅ WiFi Hotspot सेटअप पूरा!"
echo ""
echo "📡 WiFi Name: $SSID"
echo "🔑 Password: $PASSWORD"
echo "🌐 GramAI URL: http://$IP_ADDRESS:8000"
echo ""
echo "📱 अपने मोबाइल से '$SSID' WiFi से जुड़ें"
echo "   फिर ब्राउज़र में खोलें: http://$IP_ADDRESS:8000"
echo "==============================================${NC}"
