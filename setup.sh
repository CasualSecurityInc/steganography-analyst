#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

SKILL_DIR="$SCRIPT_DIR/steganography-analyst"
BIN_DIR="$SKILL_DIR/scripts/bin"
LIB_DIR="$SKILL_DIR/scripts/lib"
VENV_DIR="$SCRIPT_DIR/.venv"
ENV_FILE="$SKILL_DIR/scripts/env.sh"

mkdir -p "$BIN_DIR" "$LIB_DIR"

# ── Platform detection ──────────────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS" in
    Darwin) PLATFORM="darwin" ;;
    Linux)  PLATFORM="linux" ;;
    *)      echo "Unsupported OS: $OS"; exit 1 ;;
esac
case "$ARCH" in
    arm64|aarch64) ARCH_NAME="arm64" ;;
    x86_64)        ARCH_NAME="amd64" ;;
    *)             echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo "=== steganography-analyst setup ($PLATFORM-$ARCH_NAME) ==="
echo ""

# ── Bootstrap uv ────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "[1/6] Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if ! command -v uv &>/dev/null; then
        echo "ERROR: uv installation failed. Install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
else
    echo "[1/6] uv found: $(command -v uv)"
fi

# ── Python venv + packages ──────────────────────────────────────────
echo "[2/6] Setting up Python venv and installing tools..."
if [ ! -d "$VENV_DIR" ]; then
    uv venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
uv pip install stegoveritas binwalk Pillow numpy 2>&1 | grep -E "^( \+|All)" || true
deactivate

# Check libmagic (required by stegoveritas at runtime)
if ! "$VENV_DIR/bin/python" -c "import magic" 2>/dev/null; then
    echo "  NOTE: stegoveritas needs libmagic. Install with:"
    if [ "$PLATFORM" = "darwin" ]; then
        echo "    brew install libmagic"
    else
        echo "    apt install libmagic1"
    fi
fi

# ── jsteg (pre-built Go binary) ─────────────────────────────────────
echo "[3/6] Downloading jsteg..."
JSTEG_URL="https://github.com/lukechampine/jsteg/releases/download/v0.3.0/jsteg-${PLATFORM}-${ARCH_NAME}"
if [ ! -f "$BIN_DIR/jsteg" ]; then
    curl -sL "$JSTEG_URL" -o "$BIN_DIR/jsteg"
    chmod +x "$BIN_DIR/jsteg"
    echo "  jsteg installed to $BIN_DIR/jsteg"
else
    echo "  jsteg already present"
fi

# ── StegSolve (Java JAR, from GitHub mirror) ────────────────────────
echo "[4/6] Downloading StegSolve..."
STEGSOLVE_URL="https://github.com/Giotino/stegsolve/releases/download/v1.4/StegSolve-1.4.jar"
if [ ! -f "$LIB_DIR/StegSolve.jar" ]; then
    if curl -sfL "$STEGSOLVE_URL" -o "$LIB_DIR/StegSolve.jar" 2>/dev/null; then
        echo "  StegSolve 1.4 downloaded to $LIB_DIR/StegSolve.jar"
    else
        echo "  WARNING: StegSolve download failed. Requires Java to run."
        echo "  Download manually: $STEGSOLVE_URL"
    fi
else
    echo "  StegSolve already present"
fi

# ── stegseek ────────────────────────────────────────────────────────
echo "[5/6] Checking stegseek..."
if command -v stegseek &>/dev/null; then
    echo "  stegseek found: $(command -v stegseek)"
elif [ "$PLATFORM" = "linux" ]; then
    echo "  Downloading stegseek .deb and extracting binary..."
    DEB_URL="https://github.com/RickdeJager/stegseek/releases/download/v0.6/stegseek_0.6-1.deb"
    DEB_TMP=$(mktemp)
    curl -sL "$DEB_URL" -o "$DEB_TMP"
    # Extract binary from .deb (ar archive → data.tar → usr/bin/stegseek)
    DEB_EXTRACT=$(mktemp -d)
    ar x "$DEB_TMP" --output="$DEB_EXTRACT" 2>/dev/null || (cd "$DEB_EXTRACT" && ar x "$DEB_TMP")
    tar xf "$DEB_EXTRACT"/data.tar* -C "$DEB_EXTRACT" 2>/dev/null
    if [ -f "$DEB_EXTRACT/usr/bin/stegseek" ]; then
        cp "$DEB_EXTRACT/usr/bin/stegseek" "$BIN_DIR/stegseek"
        chmod +x "$BIN_DIR/stegseek"
        echo "  stegseek installed to $BIN_DIR/stegseek"
    else
        echo "  WARNING: Could not extract stegseek from .deb"
    fi
    rm -rf "$DEB_TMP" "$DEB_EXTRACT"
elif [ "$PLATFORM" = "darwin" ]; then
    echo "  stegseek not available as binary for macOS."
    echo "  Install via: brew install stegseek"
fi

# ── zsteg (Ruby gem) ───────────────────────────────────────────────
echo "[6/6] Installing zsteg..."
if command -v zsteg &>/dev/null; then
    echo "  zsteg found: $(command -v zsteg)"
elif command -v gem &>/dev/null; then
    gem install --user-install zsteg 2>&1 | tail -3
    echo "  zsteg installed (user-local gem)"
else
    echo "  WARNING: Ruby/gem not found. Install Ruby first, then: gem install --user-install zsteg"
fi

# ── Generate env.sh ─────────────────────────────────────────────────
GEM_BIN=""
if command -v gem &>/dev/null; then
    GEM_USER_DIR="$(gem environment 2>/dev/null | grep 'USER INSTALLATION DIRECTORY:' | sed 's/.*: //')"
    [ -d "$GEM_USER_DIR/bin" ] && GEM_BIN="$GEM_USER_DIR/bin"
fi
cat > "$ENV_FILE" <<ENVEOF
# Source this file to add steganography-analyst tools to PATH:
#   source steganography-analyst/scripts/env.sh
export PATH="$BIN_DIR:$VENV_DIR/bin${GEM_BIN:+:$GEM_BIN}:\$PATH"
ENVEOF

# ── System tool check ───────────────────────────────────────────────
echo ""
echo "=== System tool status ==="
MISSING=()
for tool in exiftool pngcheck foremost steghide stegsnow multimon-ng; do
    if command -v "$tool" &>/dev/null; then
        echo "  [ok] $tool"
    else
        echo "  [--] $tool (not found)"
        MISSING+=("$tool")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "Missing system tools. Install with:"
    if [ "$PLATFORM" = "darwin" ]; then
        echo "  brew install ${MISSING[*]}"
    else
        echo "  # Use your package manager, e.g.:"
        echo "  apt install ${MISSING[*]}"
    fi
fi

# ── Done ────────────────────────────────────────────────────────────
echo ""
echo "=== Setup complete ==="
echo "Run: source steganography-analyst/scripts/env.sh"
echo "Then see steganography-analyst/SKILL.md for the analysis playbook."
