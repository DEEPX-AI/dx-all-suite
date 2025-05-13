#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../")

# color env settings
source ${RUNTIME_PATH}/scripts/color_env.sh

function print_color_sample() {
  name=$1
  color=$2
  echo -e "${color} ${name} ${COLOR_RESET}"
}

echo "=== color set 1 ==="
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

echo "=== color set 2 ==="
print_color_sample "COLOR_BLACK_ON_RED" "$COLOR_BLACK_ON_RED"
print_color_sample "COLOR_BLACK_ON_BLUE" "$COLOR_BLACK_ON_BLUE"
print_color_sample "COLOR_BLACK_ON_WHITE" "$COLOR_BLACK_ON_WHITE"
print_color_sample "COLOR_BLACK_ON_GREEN" "$COLOR_BLACK_ON_GREEN"
print_color_sample "COLOR_WHITE_ON_GREEN" "$COLOR_WHITE_ON_GREEN"
print_color_sample "COLOR_WHITE_ON_DARK_GREEN" "$COLOR_WHITE_ON_DARK_GREEN"
print_color_sample "COLOR_WHITE_ON_RED" "$COLOR_WHITE_ON_RED"
print_color_sample "COLOR_BLACK_ON_RED" "$COLOR_BLACK_ON_RED"
print_color_sample "COLOR_WHITE_ON_BLUE" "$COLOR_WHITE_ON_BLUE"
print_color_sample "COLOR_BLACK_ON_BLUE" "$COLOR_BLACK_ON_BLUE"
print_color_sample "COLOR_WHITE_ON_YELLOW" "$COLOR_WHITE_ON_YELLOW"
print_color_sample "COLOR_BLACK_ON_YELLOW" "$COLOR_BLACK_ON_YELLOW"
print_color_sample "COLOR_WHITE_ON_CYAN" "$COLOR_WHITE_ON_CYAN"
print_color_sample "COLOR_BLACK_ON_CYAN" "$COLOR_BLACK_ON_CYAN"
print_color_sample "COLOR_WHITE_ON_MAGENTA" "$COLOR_WHITE_ON_MAGENTA"
print_color_sample "COLOR_BLACK_ON_MAGENTA" "$COLOR_BLACK_ON_MAGENTA"
print_color_sample "COLOR_WHITE_ON_GRAY" "$COLOR_WHITE_ON_GRAY"
print_color_sample "COLOR_BLACK_ON_GRAY" "$COLOR_BLACK_ON_GRAY"

