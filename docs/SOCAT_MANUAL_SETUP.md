# Manual Socat Installation Guide

If you prefer to manually place the socat binary instead of installing it via package manager, follow these instructions for your operating system.

## 📍 Socat Directory Locations

The app looks for socat binaries in these locations:

| OS | Path |
|----|------|
| **macOS** | `~/Library/Application Support/PS_MultiInjector/socat/` |
| **Windows** | `%APPDATA%\PS_MultiInjector\socat\` |
| **Linux** | `~/.local/share/PS_MultiInjector/socat/` |

## 🐧 Linux - Manual Socat Setup

### Step 1: Create the Directory
```bash
mkdir -p ~/.local/share/PS_MultiInjector/socat
```

### Step 2: Download Socat Binary
For x86_64 (most common):
```bash
# Option A: From static-binaries
wget https://github.com/andrew-d/static-binaries/releases/download/latest/socat -O ~/.local/share/PS_MultiInjector/socat/socat-linux-x86_64

# Option B: Build from source
git clone https://github.com/craSH/socat.git
cd socat
./configure
make
```

### Step 3: Make Executable
```bash
chmod +x ~/.local/share/PS_MultiInjector/socat/socat-linux*
```

### Step 4: Verify
```bash
~/.local/share/PS_MultiInjector/socat/socat-linux-x86_64 --version
```

## 🍎 macOS - Manual Socat Setup

### Step 1: Create the Directory
```bash
mkdir -p ~/Library/Application\ Support/PS_MultiInjector/socat
```

### Step 2: Download Socat Binary

**For ARM (Apple Silicon - M1/M2/M3):**
```bash
# Option A: Homebrew (recommended)
brew install socat

# Then copy to app directory
cp $(which socat) ~/Library/Application\ Support/PS_MultiInjector/socat/socat-darwin-arm64
```

**For Intel (x86_64):**
```bash
# Option A: Homebrew (recommended)
brew install socat

# Then copy to app directory
cp $(which socat) ~/Library/Application\ Support/PS_MultiInjector/socat/socat-darwin-x86_64
```

**Option B: Manual Download**
```bash
# Download pre-built binary from static-binaries (if available)
# macOS doesn't have official pre-built binaries, so Homebrew is recommended
```

### Step 3: Make Executable
```bash
chmod +x ~/Library/Application\ Support/PS_MultiInjector/socat/socat-darwin-*
```

### Step 4: Verify
```bash
~/Library/Application\ Support/PS_MultiInjector/socat/socat-darwin-* --version
```

## 🪟 Windows - Manual Socat Setup

### Step 1: Create the Directory

**Command Prompt (cmd.exe):**
```cmd
mkdir "%APPDATA%\PS_MultiInjector\socat"
```

**PowerShell:**
```powershell
mkdir -Path "$env:APPDATA\PS_MultiInjector\socat"
```

### Step 2: Download Socat Binary

**Option A: scoop (Recommended)**
```powershell
scoop install socat

# Find where socat was installed
scoop which socat

# Copy to app directory
Copy-Item (scoop which socat) "$env:APPDATA\PS_MultiInjector\socat\socat.exe"
```

**Option B: WSL (Windows Subsystem for Linux)**
```bash
# Inside WSL
sudo apt install socat

# Then copy from WSL to Windows app folder
cp /usr/bin/socat /mnt/c/Users/YourUsername/AppData/Roaming/PS_MultiInjector/socat/socat.exe
```

**Option C: Manual Download**
```powershell
# Download from: https://github.com/andrew-d/static-binaries/releases
# Extract and rename to socat.exe
# Place in: %APPDATA%\PS_MultiInjector\socat\socat.exe
```

### Step 3: Verify
```cmd
"%APPDATA%\PS_MultiInjector\socat\socat.exe" --version
```

## ✅ Verify Installation

After placing the socat binary:

1. **Open PS MultiInjector**
2. **Look for the "Enable SOCAT" checkbox**
3. **If socat is detected:**
   - Checkbox will be enabled (clickable)
   - No popup message when you click it
4. **If socat is NOT detected:**
   - Checkbox will trigger a popup with installation instructions

## 📝 Binary Naming Convention

The app automatically looks for binaries with these names:

| OS | Filenames (in order of preference) |
|----|-----|
| **Linux** | `socat-linux-x86_64`, `socat-linux`, `socat` |
| **macOS ARM** | `socat-darwin-arm64`, `socat-mac-arm`, `socat` |
| **macOS Intel** | `socat-darwin-x86_64`, `socat-mac`, `socat` |
| **Windows** | `socat.exe` |

The app will use the **first available** binary it finds.

## 🚀 Quick Commands by OS

### Linux
```bash
mkdir -p ~/.local/share/PS_MultiInjector/socat
# Download or copy socat binary here
chmod +x ~/.local/share/PS_MultiInjector/socat/socat-linux-x86_64
```

### macOS
```bash
mkdir -p ~/Library/Application\ Support/PS_MultiInjector/socat
brew install socat
cp $(which socat) ~/Library/Application\ Support/PS_MultiInjector/socat/socat-darwin-arm64
chmod +x ~/Library/Application\ Support/PS_MultiInjector/socat/socat-darwin-*
```

### Windows (PowerShell)
```powershell
mkdir -Path "$env:APPDATA\PS_MultiInjector\socat"
scoop install socat
Copy-Item (scoop which socat) "$env:APPDATA\PS_MultiInjector\socat\socat.exe"
```

## 🔍 Troubleshooting

### Socat binary not detected after placement
- Make sure the file is executable: `chmod +x` on Linux/macOS
- Check the directory path matches exactly (case-sensitive on Linux/macOS)
- Verify filename matches the naming convention above
- Restart the app

### "Permission denied" error
```bash
# Fix executable permission
chmod +x /path/to/socat
```

### Binary version incompatibility
- Ensure the socat binary matches your system architecture:
  - macOS: `uname -m` should return `arm64` or `x86_64`
  - Linux: `uname -m` should return `x86_64`
  - Windows: Most modern systems are `x86_64`

## 📚 Additional Resources

- **Socat GitHub**: https://github.com/craSH/socat
- **Static Binaries**: https://github.com/andrew-d/static-binaries
- **Homebrew**: https://brew.sh
- **scoop**: https://scoop.sh

## ℹ️ Alternative: Use System Package Manager

For most users, installing via package manager is simpler:

```bash
# Linux
sudo apt install socat

# macOS
brew install socat

# Windows
scoop install socat
# or use WSL with: sudo apt install socat
```

The app will automatically find socat in your system PATH.
