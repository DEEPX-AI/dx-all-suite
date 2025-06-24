#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../") # Assuming color_env.sh is in scripts/ relative to this test file's parent

# color env settings
source "${RUNTIME_PATH}/scripts/color_env.sh" # Ensure this path is correct for color_env.sh

function print_color_sample() {
  name=$1
  color=$2
  # Use -n for no newline, and add a tab for alignment, then reset color
  echo -e "${color} ${name} ${COLOR_RESET}\t| ${name} Example Text"
}

echo "=== Basic Foreground Colors ==="
print_color_sample "COLOR_BLACK" "$COLOR_BLACK"
print_color_sample "COLOR_RED" "$COLOR_RED"
print_color_sample "COLOR_GREEN" "$COLOR_GREEN"
print_color_sample "COLOR_YELLOW" "$COLOR_YELLOW"
print_color_sample "COLOR_BLUE" "$COLOR_BLUE"
print_color_sample "COLOR_MAGENTA" "$COLOR_MAGENTA"
print_color_sample "COLOR_CYAN" "$COLOR_CYAN"
print_color_sample "COLOR_WHITE" "$COLOR_WHITE"
echo ""

echo "=== Bright Foreground Colors ==="
print_color_sample "COLOR_BRIGHT_BLACK" "$COLOR_BRIGHT_BLACK"
print_color_sample "COLOR_BRIGHT_RED" "$COLOR_BRIGHT_RED"
print_color_sample "COLOR_BRIGHT_GREEN" "$COLOR_BRIGHT_GREEN"
print_color_sample "COLOR_BRIGHT_YELLOW" "$COLOR_BRIGHT_YELLOW"
print_color_sample "COLOR_BRIGHT_BLUE" "$COLOR_BRIGHT_BLUE"
print_color_sample "COLOR_BRIGHT_MAGENTA" "$COLOR_BRIGHT_MAGENTA"
print_color_sample "COLOR_BRIGHT_CYAN" "$COLOR_BRIGHT_CYAN"
print_color_sample "COLOR_BRIGHT_WHITE" "$COLOR_BRIGHT_WHITE"
echo ""

echo "=== Background Colors ==="
print_color_sample "COLOR_BG_BLACK" "$COLOR_BG_BLACK"
print_color_sample "COLOR_BG_RED" "$COLOR_BG_RED"
print_color_sample "COLOR_BG_GREEN" "$COLOR_BG_GREEN"
print_color_sample "COLOR_BG_YELLOW" "$COLOR_BG_YELLOW"
print_color_sample "COLOR_BG_BLUE" "$COLOR_BG_BLUE"
print_color_sample "COLOR_BG_MAGENTA" "$COLOR_BG_MAGENTA"
print_color_sample "COLOR_BG_CYAN" "$COLOR_BG_CYAN"
print_color_sample "COLOR_BG_WHITE" "$COLOR_BG_WHITE"
echo ""

echo "=== Bright Background Colors ==="
print_color_sample "COLOR_BRIGHT_BG_BLACK" "$COLOR_BRIGHT_BG_BLACK"
print_color_sample "COLOR_BRIGHT_BG_RED" "$COLOR_BRIGHT_BG_RED"
print_color_sample "COLOR_BRIGHT_BG_GREEN" "$COLOR_BRIGHT_BG_GREEN"
print_color_sample "COLOR_BRIGHT_BG_YELLOW" "$COLOR_BRIGHT_BG_YELLOW"
print_color_sample "COLOR_BRIGHT_BG_BLUE" "$COLOR_BRIGHT_BG_BLUE"
print_color_sample "COLOR_BRIGHT_BG_MAGENTA" "$COLOR_BRIGHT_BG_MAGENTA"
print_color_sample "COLOR_BRIGHT_BG_CYAN" "$COLOR_BRIGHT_BG_CYAN"
print_color_sample "COLOR_BRIGHT_BG_WHITE" "$COLOR_BRIGHT_BG_WHITE"
echo ""

echo "=== Combined Foreground/Background Colors ==="
print_color_sample "COLOR_BRIGHT_RED_ON_BLACK" "$COLOR_BRIGHT_RED_ON_BLACK"
print_color_sample "COLOR_BRIGHT_GREEN_ON_BLACK" "$COLOR_BRIGHT_GREEN_ON_BLACK"
print_color_sample "COLOR_BRIGHT_YELLOW_ON_BLACK" "$COLOR_BRIGHT_YELLOW_ON_BLACK"
print_color_sample "COLOR_BRIGHT_BLUE_ON_BLACK" "$COLOR_BRIGHT_BLUE_ON_BLACK"
print_color_sample "COLOR_BRIGHT_MAGENTA_ON_BLACK" "$COLOR_BRIGHT_MAGENTA_ON_BLACK"
print_color_sample "COLOR_BRIGHT_CYAN_ON_BLACK" "$COLOR_BRIGHT_CYAN_ON_BLACK"
print_color_sample "COLOR_BRIGHT_WHITE_ON_BLACK" "$COLOR_BRIGHT_WHITE_ON_BLACK"
print_color_sample "COLOR_RED_ON_BLACK" "$COLOR_RED_ON_BLACK"
print_color_sample "COLOR_BLUE_ON_BLACK" "$COLOR_BLUE_ON_BLACK"
print_color_sample "COLOR_WHITE_ON_BLACK" "$COLOR_WHITE_ON_BLACK"

print_color_sample "COLOR_BLACK_ON_RED" "$COLOR_BLACK_ON_RED"
print_color_sample "COLOR_BLACK_ON_BLUE" "$COLOR_BLACK_ON_BLUE"
print_color_sample "COLOR_BLACK_ON_WHITE" "$COLOR_BLACK_ON_WHITE"
print_color_sample "COLOR_BLACK_ON_GREEN" "$COLOR_BLACK_ON_GREEN"
print_color_sample "COLOR_WHITE_ON_GREEN" "$COLOR_WHITE_ON_GREEN"
print_color_sample "COLOR_WHITE_ON_DARK_GREEN" "$COLOR_WHITE_ON_DARK_GREEN"
print_color_sample "COLOR_WHITE_ON_RED" "$COLOR_WHITE_ON_RED"
print_color_sample "COLOR_WHITE_ON_BLUE" "$COLOR_WHITE_ON_BLUE"
print_color_sample "COLOR_BLACK_ON_YELLOW" "$COLOR_BLACK_ON_YELLOW"
print_color_sample "COLOR_WHITE_ON_YELLOW" "$COLOR_WHITE_ON_YELLOW"
print_color_sample "COLOR_WHITE_ON_CYAN" "$COLOR_WHITE_ON_CYAN"
print_color_sample "COLOR_BLACK_ON_CYAN" "$COLOR_BLACK_ON_CYAN"
print_color_sample "COLOR_WHITE_ON_MAGENTA" "$COLOR_WHITE_ON_MAGENTA"
print_color_sample "COLOR_BLACK_ON_MAGENTA" "$COLOR_BLACK_ON_MAGENTA"
print_color_sample "COLOR_WHITE_ON_GRAY" "$COLOR_WHITE_ON_GRAY"
print_color_sample "COLOR_BLACK_ON_GRAY" "$COLOR_BLACK_ON_GRAY"
echo ""

echo "=== Text Styles ==="
print_color_sample "COLOR_BOLD" "${COLOR_BOLD}"
print_color_sample "COLOR_UNDERLINE" "${COLOR_UNDERLINE}"
print_color_sample "COLOR_BLINK" "${COLOR_BLINK}"
print_color_sample "COLOR_INVERSE" "${COLOR_INVERSE}"
echo ""

echo "=== Tag Definitions ==="
echo -e "${TAG_START} This is a START tag example."
echo -e "${TAG_DONE} This is a DONE tag example."
echo -e "${TAG_SUCC} This is a SUCC tag example."
echo -e "${TAG_ERROR} This is an ERROR tag example."
echo -e "${TAG_INFO} This is an INFO tag example."
echo -e "${TAG_WARN} This is a WARN tag example."
echo -e "${TAG_SKIP} This is a SKIP tag example."
echo ""
