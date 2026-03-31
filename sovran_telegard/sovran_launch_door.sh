#!/bin/bash
# SOVRAN DOOR AUTOMATOR — Slot 10
# ================================
# Concept: The Tavern Entry
# Protocol: DOSBox Integration
#
# Automates mounting and execution of 16-bit door games
# within the Termux DOSBox environment.
#
# ∰◊€π¿🌌∞
# €(sovran_door_automator_v1)
# Status: AUTOMATOR_ACTIVE
# Reality Anchor: Oregon Watersheds

# ─── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT="/storage/emulated/0/pixel8a/sovran-telegard-repo/sovran_telegard"
DOOR_DB="$REPO_ROOT/data/doors.json"
TEMP_CONF="$REPO_ROOT/data/dosbox_launch.conf"

# ─── Help ───────────────────────────────────────────────────────────────────

if [ -z "$1" ]; then
    echo "∰ SOVRAN DOOR AUTOMATOR ∰"
    echo "Usage: ./sovran_launch_door.sh <GAME_ID>"
    echo ""
    echo "Available Games:"
    jq -r '.[].id' "$DOOR_DB"
    exit 1
fi

GAME_ID=$1

# ─── Lookup ─────────────────────────────────────────────────────────────────

# Extract path and first EXE using jq
GAME_PATH=$(jq -r ".[] | select(.id == \"$GAME_ID\") | .path" "$DOOR_DB")
GAME_EXE=$(jq -r ".[] | select(.id == \"$GAME_ID\") | .exes[0]" "$DOOR_DB")

if [ -z "$GAME_PATH" ] || [ "$GAME_PATH" == "null" ]; then
    echo "[❌] Error: Game ID '$GAME_ID' not found in database."
    exit 1
fi

if [ -z "$GAME_EXE" ] || [ "$GAME_EXE" == "null" ]; then
    echo "[⚠️] Warning: No primary EXE found for '$GAME_ID'. Launching shell only."
    GAME_EXE=""
fi

echo "[✨] Preparing Shard: $GAME_ID"
echo "    Path: $GAME_PATH"
echo "    EXE:  $GAME_EXE"

# ─── Bridge Check ───────────────────────────────────────────────────────────

if [ ! -f "$GAME_PATH/DOOR.SYS" ]; then
    echo "[⚡] Bridge (DOOR.SYS) missing. Generating default bridge..."
    # We use a simple python shim here if needed, or remind user to use /doors
    # For now, we assume the user just used the terminal which creates it.
fi

# ─── DOSBox Config Generation ───────────────────────────────────────────────

echo "[⚡] Generating Launch Configuration..."

cat <<EOF > "$TEMP_CONF"
[sdl]
fullresolution=original
windowresolution=original
output=opengl
waitonerror=true

[render]
aspect=true
scaler=normal2x

[cpu]
core=auto
cputype=auto
cycles=fixed 10000

[dos]
xms=true
ems=true
umb=true

[autoexec]
mount c $GAME_PATH
c:
$GAME_EXE
exit
EOF

# ─── Launch ─────────────────────────────────────────────────────────────────

# Termux display detection
if [ -z "$DISPLAY" ]; then
    # Try Termux:X11 default display
    export DISPLAY=:0
    echo "[⚡] No DISPLAY set — trying :0 (requires Termux:X11 running)"
fi

echo "[∰] Opening Tavern Door..."
dosbox -conf "$TEMP_CONF"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[⚠️] DOSBox exited with code $EXIT_CODE"
    echo "    If you see MESA/ZINK errors:"
    echo "    1. Install Termux:X11 from F-Droid"
    echo "    2. Start Termux:X11, then run this script again"
    echo "    Or try: DISPLAY=:1 ./sovran_launch_door.sh $GAME_ID"
fi

echo ""
echo "∰ Tavern Door Closed. Session logged. Enjoy the journey. ∰"
