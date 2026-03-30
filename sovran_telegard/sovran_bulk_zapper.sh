#!/bin/bash
# SOVRAN BULK ZAPPER
# Zaps all files in the Aquifer cold storage into Sovran Telegard.

AQUIFER_COLD="/storage/emulated/0/pixel8a/_pixelator/pixelate/the_aquifer/cold/"

echo "∰ SOVRAN BULK ZAPPER ACTIVATED ∰"
echo "--------------------------------"

for f in $(ls $AQUIFER_COLD); do
    if [[ $f == *.zip ]]; then
        echo "Processing $f..."
        PYTHONPATH=Q/runexusiam/sovran_telegard/ python3 Q/runexusiam/sovran_telegard/sovran_zapper.py "$f"
    fi
done

echo "--------------------------------"
echo "∰ BULK ZAP COMPLETE ∰"
