#!/usr/bin/env bash 
LRC_PATH=$(realpath "$1")
REF_PROMPT=$2

cd "$(dirname "$0")"
cd ../libs/DiffRhythm

export PYTHONPATH=$PYTHONPATH:$PWD
export CUDA_VISIBLE_DEVICES=0
export HF_HUB_ENABLE_HF_TRANSFER=1


# Define Color Variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[1;34m' # Bold Blue
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color (reset)

# Check if the LRC_PATH is passed
if [ -z "$LRC_PATH" ]; then
    printf "%b" "${GREEN}Using default LRC path: infer/example/eg_en_full.lrc.${NC}\n"
    LRC_PATH="infer/example/eg_en_full.lrc"
else
    if [ -f "$LRC_PATH" ]; then
        printf "%b" "${GREEN}Using provided LRC path: $LRC_PATH${NC}\n"
    else
        printf "%b" "${RED}Error: LRC file not found at $LRC_PATH.${NC}\n"
        exit 1
    fi
fi

if [ -z "$REF_PROMPT" ]; then
    printf "%b" "${YELLOW}Using default reference prompt: classical genres, hopeful mood, piano.${NC}\n"
    REF_PROMPT="classical genres, hopeful mood, piano."
    # echo "Please provide a reference prompt."
    # echo "Usage: $0 <ref_prompt>"
    # exit 1
else
    printf "%b" "${GREEN}Using provided reference prompt: $REF_PROMPT${NC}\n"
fi


if [[ "$OSTYPE" =~ ^darwin ]]; then
    export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/Cellar/espeak-ng/1.52.0/lib/libespeak-ng.dylib
fi

# --lrc-path infer/example/eg_en_full.lrc \
uv run python3 infer/infer.py \
    --lrc-path "${LRC_PATH}" \
    --ref-prompt "${REF_PROMPT}" \
    --audio-length 285 \
    --repo_id ASLP-lab/DiffRhythm-full \
    --output-dir infer/example/output \
    --chunked
