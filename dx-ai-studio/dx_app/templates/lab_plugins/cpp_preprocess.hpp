#pragma once
#include <string>

namespace dx_app_lab {
struct PluginContext;

// TODO: Implement this plugin before adding it to a runnable workflow.
std::string preprocess(const std::string& input_path, const PluginContext& context);
}  // namespace dx_app_lab