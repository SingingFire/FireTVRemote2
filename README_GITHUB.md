# Fire TV Remote - Bluetooth Control App

Android app to control Fire TV devices via Bluetooth HID protocol.

## Features

- **D-Pad Navigation**: Up, Down, Left, Right, OK
- **System Controls**: Home, Back, Menu
- **Media Controls**: Play/Pause, Rewind, Fast Forward
- **Bluetooth Connection**: Pairs directly with Fire TV
- **Clean UI**: Simple, functional remote interface

## Installation

### Option 1: Download APK (Easiest)
1. Go to [Actions](../../actions) tab
2. Click latest successful build
3. Download APK from Artifacts section
4. Install on your Android phone

### Option 2: Build Yourself
Requires WSL2 or Linux:
```bash
buildozer android debug
```

## Setup

### 1. Pair Fire TV
- Fire TV: Settings → Bluetooth → Add Device
- Phone: Settings → Bluetooth → Pair with Fire TV

### 2. Open App
- Tap "Connect to Fire TV"
- Select your Fire TV
- Start controlling!

## Requirements

- Android 5.0+ (API 21+)
- Fire TV with Bluetooth enabled
- Both devices paired via Bluetooth

## How It Works

Uses Android Bluetooth HID (Human Interface Device) protocol to send keycodes directly to Fire TV, just like the official remote.

## Development

- **Language**: Python 3
- **Framework**: Kivy
- **Build Tool**: Buildozer
- **Target**: Android ARM64/ARMv7

## Files

- `main.py` - Main application code
- `buildozer.spec` - Build configuration
- `.github/workflows/build.yml` - GitHub Actions workflow

## Testing

Mock version for UI testing available in `main_pydroid.py` (works in Pydroid 3 without Bluetooth permissions).

## License

Open source - modify and distribute freely.

## Support

Having issues? Check the build logs in GitHub Actions for detailed error messages.

Built with ❤️ for Fire TV users who want a simple backup remote on their phone.
