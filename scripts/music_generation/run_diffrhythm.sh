#!/usr/bin/env bash

# --- Default Values ---
DEFAULT_LRC_PATH="infer/example/eg_en_full.lrc"
DEFAULT_REF_PROMPT="classical genres, hopeful mood, piano."
DEFAULT_REF_AUDIO_PATH="" # Default to empty, meaning ref-prompt will be used unless overridden
DEFAULT_AUDIO_LENGTH="285" # Default from original script
DEFAULT_REPO_ID="ASLP-lab/DiffRhythm-full" # Default from original script
DEFAULT_OUTPUT_DIR="infer/example/output" # Default from original script
DEFAULT_OUTPUT_FILE_NAME="output.wav" # Default from original script
DEFAULT_CHUNKED=true # Default from original script (presence of --chunked)

# Initialize variables with defaults
lrc_path_arg=""
ref_prompt_arg=""
ref_audio_path_arg=""
audio_length_arg=""
repo_id_arg=""
output_dir_arg=""
output_file_name_arg=$DEFAULT_OUTPUT_FILE_NAME
chunked_arg=$DEFAULT_CHUNKED # Boolean flag handling

# --- Argument Parsing with getopt ---
# Define short and long options
# Note: getopt syntax varies slightly between Linux (util-linux) and macOS (BSD)
# This uses Linux getopt syntax. For macOS, install gnu-getopt: brew install gnu-getopt
# and potentially call it as `gnu-getopt` or add it to PATH first.
# Options ending with ':' expect an argument. 'chunked' is a flag.
SHORT_OPTS="l:p:a:L:R:O:f:ch" # Added 'f' for output file name, 'a' for ref-audio, 'c' for chunked flag, 'h' for help
LONG_OPTS="lrc-path:,ref-prompt:,ref-audio-path:,audio-length:,repo-id:,output-dir:,output-file-name:,chunked,help"

# Check if getopt is available
if ! command -v getopt &> /dev/null; then
    echo "Error: getopt command not found. Please install it (e.g., util-linux on Linux, gnu-getopt on macOS)."
    exit 1
fi

# Use getopt to parse options
# The -- means arguments after it are not options (useful if paths start with -)
# Note the use of quotes to handle spaces in arguments
PARSED_OPTS=$(getopt --options $SHORT_OPTS --longoptions $LONG_OPTS --name "$0" -- "$@")

# Check if getopt failed
if [[ $? -ne 0 ]]; then
    # getopt prints error message
    exit 2
fi

# Apply the parsed options to the shell's arguments ($@)
eval set -- "$PARSED_OPTS"

# Process the parsed options
while true; do
    case "$1" in
        -l|--lrc-path)
            lrc_path_arg="$2"
            shift 2
            ;;
        -p|--ref-prompt)
            ref_prompt_arg="$2"
            shift 2
            ;;
        -a|--ref-audio-path)
            ref_audio_path_arg="$2"
            shift 2
            ;;
        -L|--audio-length)
            audio_length_arg="$2"
            shift 2
            ;;
        -R|--repo-id)
            repo_id_arg="$2"
            shift 2
            ;;
        -O|--output-dir)
            output_dir_arg="$2"
            shift 2
            ;;
        -f|--output-file-name)
            output_file_name_arg="$2"
            shift 2
            ;;
        -c|--chunked)
            # If --chunked is present, set to true. If not, it remains default.
            # If you want a --no-chunked option, that requires more logic.
            chunked_arg=true
            shift # Shift only 1 because it's a flag
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -l, --lrc-path FILE         Path to lyrics file (Default: $DEFAULT_LRC_PATH)"
            echo "  -p, --ref-prompt TEXT       Reference text prompt (Default: '$DEFAULT_REF_PROMPT')"
            echo "  -a, --ref-audio-path FILE   Path to reference audio file (Overrides ref-prompt if provided)"
            echo "  -L, --audio-length {95|285} Audio length in seconds (Default: $DEFAULT_AUDIO_LENGTH)"
            echo "  -R, --repo-id ID            Hugging Face model repo ID (Default: $DEFAULT_REPO_ID)"
            echo "  -O, --output-dir DIR        Output directory (Default: $DEFAULT_OUTPUT_DIR)"
            echo "  -c, --chunked               Enable chunked decoding (Default: $DEFAULT_CHUNKED)"
            echo "  -h, --help                  Show this help message"
            exit 0
            ;;
        --) # End of options
            shift
            break
            ;;
        *) # Should not happen with getopt
            echo "Internal error!"
            exit 1
            ;;
    esac
done

# --- Set Working Directory and Environment ---
# Get the directory containing this script
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
# Navigate to the expected DiffRhythm root relative to the script's parent
# TARGET_DIR=$(cd "${SCRIPT_DIR}/../../vendor/DiffRhythm" && pwd)
TARGET_DIR=$(cd "${SCRIPT_DIR}/../" && pwd)

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory not found: $TARGET_DIR"
    exit 1
fi

cd "$TARGET_DIR"
echo "Changed working directory to: $PWD"

export PYTHONPATH=$PYTHONPATH:$PWD
export CUDA_VISIBLE_DEVICES=0 # Keep default or allow override via env var? Keeping default.
export HF_HUB_ENABLE_HF_TRANSFER=1

if [[ "$OSTYPE" =~ ^darwin ]]; then
    # Consider making this path configurable or checking common locations
    export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/Cellar/espeak-ng/1.52.0/lib/libespeak-ng.dylib
fi

# --- Define Color Variables ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[1;34m' # Bold Blue
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color (reset)

# --- Final Variable Assignment and Validation ---
LRC_PATH=${lrc_path_arg:-$DEFAULT_LRC_PATH}
REF_PROMPT=${ref_prompt_arg:-$DEFAULT_REF_PROMPT}
REF_AUDIO_PATH=${ref_audio_path_arg:-$DEFAULT_REF_AUDIO_PATH}
AUDIO_LENGTH=${audio_length_arg:-$DEFAULT_AUDIO_LENGTH}
REPO_ID=${repo_id_arg:-$DEFAULT_REPO_ID}
OUTPUT_DIR=${output_dir_arg:-$DEFAULT_OUTPUT_DIR}
OUTPUT_FILE_NAME=${output_file_name_arg:-$DEFAULT_OUTPUT_FILE_NAME}
CHUNKED=$chunked_arg

# Validate LRC Path (only if it wasn't the default one implicitly used)
if [ -n "$lrc_path_arg" ]; then
    # Resolve the path similar to `realpath` for checking
    RESOLVED_LRC_PATH=$(realpath "$LRC_PATH" 2>/dev/null)
    if [ -z "$RESOLVED_LRC_PATH" ] || [ ! -f "$RESOLVED_LRC_PATH" ]; then
        printf "%b" "${RED}Error: Provided LRC file not found or invalid path: $LRC_PATH${NC}\n"
        exit 1
    fi
    LRC_PATH=$RESOLVED_LRC_PATH # Use the resolved path
    printf "%b" "${GREEN}Using provided LRC path: $LRC_PATH${NC}\n"
else
    printf "%b" "${GREEN}Using default LRC path (relative to CWD): $LRC_PATH${NC}\n"
    # Optional: check if default exists relative to current $PWD
    # if [ ! -f "$LRC_PATH" ]; then ... fi
fi

# Validate Audio Length
if [[ "$AUDIO_LENGTH" != "95" && "$AUDIO_LENGTH" != "285" ]]; then
    printf "%b" "${RED}Error: Invalid audio-length '$AUDIO_LENGTH'. Must be 95 or 285.${NC}\n"
    exit 1
fi

# Validate Reference Input (ensure only one is effectively used by the python script)
if [ -n "$REF_AUDIO_PATH" ]; then
    RESOLVED_REF_AUDIO_PATH=$(realpath "$REF_AUDIO_PATH" 2>/dev/null)
     if [ -z "$RESOLVED_REF_AUDIO_PATH" ] || [ ! -f "$RESOLVED_REF_AUDIO_PATH" ]; then
        printf "%b" "${RED}Error: Provided reference audio file not found or invalid path: $REF_AUDIO_PATH${NC}\n"
        exit 1
    fi
    REF_AUDIO_PATH=$RESOLVED_REF_AUDIO_PATH # Use resolved path
    printf "%b" "${GREEN}Using provided reference audio path: $REF_AUDIO_PATH${NC}\n"
    # If audio path is given, clear the prompt to mimic python script logic
    # (assuming infer.py prioritizes ref_audio_path if both are somehow passed)
    REF_PROMPT=""
elif [ -n "$ref_prompt_arg" ]; then
     printf "%b" "${GREEN}Using provided reference prompt: $REF_PROMPT${NC}\n"
else
     printf "%b" "${YELLOW}Using default reference prompt: $REF_PROMPT${NC}\n"
fi


printf "%b" "${BLUE}Final Configuration:${NC}\n"
printf "%b" "  LRC Path:       $LRC_PATH\n"
printf "%b" "  Ref Prompt:     $REF_PROMPT\n"
printf "%b" "  Ref Audio Path: $REF_AUDIO_PATH\n"
printf "%b" "  Audio Length:   $AUDIO_LENGTH\n"
printf "%b" "  Repo ID:        $REPO_ID\n"
printf "%b" "  Output Dir:     $OUTPUT_DIR\n"
printf "%b" "  Output File:    $OUTPUT_FILE_NAME\n"
printf "%b" "  Chunked:        $CHUNKED\n"

# --- Construct Python Command ---
PYTHON_CMD=(uv run infer/infer.py) # Use array for safety with paths/args

if [ -n "$LRC_PATH" ]; then
    PYTHON_CMD+=(--lrc-path "$LRC_PATH")
fi
if [ -n "$REF_PROMPT" ]; then
    PYTHON_CMD+=(--ref-prompt "$REF_PROMPT")
fi
if [ -n "$REF_AUDIO_PATH" ]; then
    PYTHON_CMD+=(--ref-audio-path "$REF_AUDIO_PATH")
fi
if [ "$CHUNKED" = true ]; then
    PYTHON_CMD+=(--chunked)
fi
PYTHON_CMD+=(--audio-length "$AUDIO_LENGTH")
PYTHON_CMD+=(--repo_id "$REPO_ID")
PYTHON_CMD+=(--output-dir "$OUTPUT_DIR") # Pass relative or absolute path
PYTHON_CMD+=(--output-file-name "$OUTPUT_FILE_NAME") # Pass relative or absolute path

# --- Execute Python Script ---
printf "\n%b" "${CYAN}Executing Python script...${NC}\n"
# Use "${PYTHON_CMD[@]}" to correctly handle spaces in arguments
"${PYTHON_CMD[@]}"

# Capture exit status
EXIT_STATUS=$?

if [ $EXIT_STATUS -eq 0 ]; then
    printf "\n%b" "${GREEN}Python script finished successfully.${NC}\n"
else
    printf "\n%b" "${RED}Python script failed with exit code $EXIT_STATUS.${NC}\n"
fi

exit $EXIT_STATUS