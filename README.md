# steganography-analyst

[![skills.sh](https://skills.sh/b/CasualSecurityInc/steganography-analyst)](https://skills.sh/CasualSecurityInc/steganography-analyst)

Two complementary AI agent skills for steganography — detection and extraction. Designed for CTF challenges, digital forensics, and security research.

| Skill | Purpose |
|-------|---------|
| **steganalysis** | Detection-first: is something hidden? Where? What signals indicate it? |
| **steganography-analyst** | Extraction: get the hidden data out using the right tools. |

## Quick start

```bash
./setup.sh                                     # install tools project-locally (no sudo)
source steganography-analyst/scripts/env.sh     # add tools to PATH
```

Then point your agent at the skill that matches the task:
- `steganalysis/SKILL.md` — "Is there hidden data here?"
- `steganography-analyst/SKILL.md` — "How do I extract it?"

## Installation

```bash
npx skills add CasualSecurityInc/steganography-analyst
```

## Skills in this repo

### steganalysis

Detection tactics — contextual analysis, structural anomalies, statistical tells, and modern AI-based steganography awareness. No tools required; this skill is about reasoning and observation.

```
steganalysis/
├── SKILL.md                        # Detection decision framework
└── references/
    ├── MODERN_STEGO.md             # Neural/adversarial stego — what changed and why it matters
    └── DETECTION_SIGNALS.md        # Catalog of specific signals by file type
```

### steganography-analyst

Extraction playbook — decision tree, tool commands, and bundled Python scripts for pulling hidden data out of files.

```
steganography-analyst/
├── SKILL.md                        # Decision tree + when-to-use
├── scripts/                        # 6 bundled Python tools
│   ├── bit_plane_extract.py        # Bit plane analysis (StegSolve replacement)
│   ├── png_crc_fix.py              # PNG dimension brute-forcer
│   ├── wavsteg.py                  # WAV LSB extraction
│   ├── wav_header_check.py         # WAV appended data detector
│   ├── zero_width_decode.py        # Zero-width Unicode decoder
│   └── homoglyph_detect.py         # Lookalike character detector
└── references/
    ├── COMMANDS.md                 # Full per-tool command reference
    ├── SETUP.md                    # Manual installation fallback
    └── WORKFLOWS.md                # Step-by-step analysis procedures
```

## External tools (installed by setup.sh)

| Tool | Install method |
|------|---------------|
| [stegoveritas](https://github.com/bannsec/stegoveritas) | `uv pip install` |
| [binwalk](https://github.com/ReFirmLabs/binwalk) | `uv pip install` |
| [zsteg](https://github.com/zed-0xff/zsteg) | `gem install --user-install` |
| [jsteg](https://github.com/lukechampine/jsteg) | Pre-built binary |
| [stegseek](https://github.com/RickdeJager/stegseek) | Binary (Linux) / Docker (macOS) |
| [StegSolve](https://github.com/Giotino/stegsolve) | JAR download (optional, needs Java) |

## Design principles

- **Project-local only** — everything installs into `.venv/` and `scripts/`, nothing goes system-wide
- **Progressive disclosure** — SKILL.md is the entry point, references load on demand
- **Detection before extraction** — steganalysis skill determines IF data is hidden; steganography-analyst determines HOW to extract it
- **`uv` over `pip`** — Python packages managed via uv in a project venv
- **Bundled where possible** — 6 Python scripts ship with the repo, stdlib-only
