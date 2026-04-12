#!/bin/bash
# ============================================================
# GramAI - Build Android APK using Capacitor
# Prerequisites: Node.js, Android Studio, Android SDK
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MOBILE_DIR="$PROJECT_DIR/mobile"

echo "=========================================="
echo "  GramAI - Android APK Build"
echo "=========================================="

# Check prerequisites
echo -e "\n${GREEN}[1/6] Checking prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is required. Install from https://nodejs.org${NC}"
    exit 1
fi
echo "  Node.js: $(node --version)"

if ! command -v npx &> /dev/null; then
    echo -e "${RED}npx is required. Install Node.js LTS.${NC}"
    exit 1
fi

# Check Android SDK
if [ -z "$ANDROID_HOME" ] && [ -z "$ANDROID_SDK_ROOT" ]; then
    echo -e "${YELLOW}  Warning: ANDROID_HOME not set. You'll need Android Studio.${NC}"
else
    echo "  Android SDK: ${ANDROID_HOME:-$ANDROID_SDK_ROOT}"
fi

# Step 2: Install Capacitor dependencies
echo -e "\n${GREEN}[2/6] Installing Capacitor...${NC}"
cd "$MOBILE_DIR"
npm install

# Step 3: Initialize Capacitor
echo -e "\n${GREEN}[3/6] Initializing Capacitor...${NC}"
if [ ! -d "android" ]; then
    npx cap add android
fi

# Step 4: Update Capacitor config
echo -e "\n${GREEN}[4/6] Syncing web assets...${NC}"
npx cap sync android

# Step 5: Copy icons to Android
echo -e "\n${GREEN}[5/6] Copying app icons...${NC}"
ICON_SRC="$PROJECT_DIR/frontend/assets"
ANDROID_RES="$MOBILE_DIR/android/app/src/main/res"

if [ -d "$ANDROID_RES" ]; then
    mkdir -p "$ANDROID_RES/mipmap-mdpi"
    mkdir -p "$ANDROID_RES/mipmap-hdpi"
    mkdir -p "$ANDROID_RES/mipmap-xhdpi"
    mkdir -p "$ANDROID_RES/mipmap-xxhdpi"
    mkdir -p "$ANDROID_RES/mipmap-xxxhdpi"

    cp "$ICON_SRC/icon-72.png"  "$ANDROID_RES/mipmap-mdpi/ic_launcher.png" 2>/dev/null || true
    cp "$ICON_SRC/icon-96.png"  "$ANDROID_RES/mipmap-hdpi/ic_launcher.png" 2>/dev/null || true
    cp "$ICON_SRC/icon-144.png" "$ANDROID_RES/mipmap-xhdpi/ic_launcher.png" 2>/dev/null || true
    cp "$ICON_SRC/icon-192.png" "$ANDROID_RES/mipmap-xxhdpi/ic_launcher.png" 2>/dev/null || true
    cp "$ICON_SRC/icon-512.png" "$ANDROID_RES/mipmap-xxxhdpi/ic_launcher.png" 2>/dev/null || true
    echo "  Icons copied to Android resources"
fi

# Step 6: Build APK
echo -e "\n${GREEN}[6/6] Building APK...${NC}"
echo "Opening Android Studio... Build the APK from there."
echo "Or run: cd mobile/android && ./gradlew assembleDebug"
npx cap open android 2>/dev/null || echo "Run 'npx cap open android' in the mobile/ directory"

echo ""
echo "=========================================="
echo -e "${GREEN}  Build setup complete!${NC}"
echo ""
echo "  To build APK manually:"
echo "  cd mobile/android"
echo "  ./gradlew assembleDebug"
echo ""
echo "  APK will be at:"
echo "  mobile/android/app/build/outputs/apk/debug/app-debug.apk"
echo "=========================================="
