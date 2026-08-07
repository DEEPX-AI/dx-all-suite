#pragma once
#include <string>

namespace dx_app_lab {
struct PluginContext;

// TODO: Implement this plugin before adding it to a runnable workflow.
std::string postprocess(const std::string& output_path, const PluginContext& context);
}  // namespace dx_app_lab