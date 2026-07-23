/*
 * dx_npu_stats.cpp
 * Helper: queries NPU DRAM usage, per-core utilization via dxrt IPC,
 * and device info (firmware, chip type, DDR, etc.) via DeviceStatus API.
 *
 * Usage: dx_npu_stats [device_id] [num_cores]
 * Output: JSON with dram, utilization, and device_info fields.
 */
#include <iostream>
#include <cstdlib>
#include <stdexcept>
#include <vector>
#include <string>
#include "dxrt/ipc_wrapper/ipc_client_wrapper.h"
#include "dxrt/ipc_wrapper/ipc_message.h"
#include "dxrt/device_info_status.h"

static std::string escapeJson(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (c == '\n') out += "\\n";
        else out += c;
    }
    return out;
}

int main(int argc, char* argv[])
{
    int deviceId  = (argc > 1) ? std::atoi(argv[1]) : 0;
    int numCores  = (argc > 2) ? std::atoi(argv[2]) : 4;

    dxrt::IPCClientWrapper wrapper(dxrt::IPCDefaultType(), getpid());
    wrapper.Initialize(false);

    auto sendReq = [&](dxrt::REQUEST_CODE code, uint32_t dev, uint64_t data) -> int64_t {
        dxrt::IPCClientMessage  req;
        dxrt::IPCServerMessage  res;
        req.code     = code;
        req.deviceId = static_cast<uint32_t>(dev);
        req.data     = data;
        req.pid      = getpid();
        wrapper.SendToServer(res, req);
        if (res.result != 0) return -1;
        return static_cast<int64_t>(res.data);
    };

    // DRAM usage (bytes)
    int64_t used_bytes  = -1;
    int64_t free_bytes  = -1;
    try { used_bytes = sendReq(dxrt::REQUEST_CODE::VIEW_USED_MEMORY,  deviceId, 10); } catch(...) {}
    try { free_bytes = sendReq(dxrt::REQUEST_CODE::VIEW_FREE_MEMORY,  deviceId, 10); } catch(...) {}

    int64_t total_bytes = (used_bytes >= 0 && free_bytes >= 0) ? used_bytes + free_bytes : -1;
    double  dram_pct    = (total_bytes > 0) ? (100.0 * used_bytes / total_bytes) : -1.0;

    // Per-core utilization (%)
    std::vector<int64_t> util(numCores, -1);
    for (int c = 0; c < numCores; ++c) {
        try { util[c] = sendReq(dxrt::REQUEST_CODE::GET_USAGE, deviceId, c); } catch(...) {}
    }

    // Device info via DeviceStatus API
    std::string fw_ver = "", dev_type = "", dev_variant = "", board_type = "";
    std::string mem_type = "", info_str = "";
    int64_t mem_size = -1;
    int mem_freq = -1;
    std::vector<uint32_t> ddr_status(4, 0);
    std::vector<uint32_t> ddr_sbe(4, 0);
    std::vector<uint32_t> ddr_dbe(4, 0);
    bool has_device_info = false;

    try {
        auto ds = dxrt::DeviceStatus::GetCurrentStatus(deviceId);
        fw_ver      = ds.FirmwareVersionStr();
        dev_type    = ds.DeviceTypeStr();
        dev_variant = ds.DeviceVariantStr();
        board_type  = ds.BoardTypeStr();
        mem_type    = ds.MemoryTypeStr();
        mem_size    = ds.MemorySize();
        mem_freq    = ds.MemoryFrequency();

        const auto& st = ds.Status();
        for (int i = 0; i < 4; ++i) {
            ddr_status[i] = st.ddr_status[i];
            ddr_sbe[i]    = st.ddr_sbe_cnt[i];
            ddr_dbe[i]    = st.ddr_dbe_cnt[i];
        }
        has_device_info = true;
    } catch (...) {}

    // Output JSON
    std::cout << "{"
              << "\"dram_used_mb\":"  << (used_bytes  >= 0 ? used_bytes  / (1024*1024) : -1) << ","
              << "\"dram_free_mb\":"  << (free_bytes  >= 0 ? free_bytes  / (1024*1024) : -1) << ","
              << "\"dram_total_mb\":" << (total_bytes >= 0 ? total_bytes / (1024*1024) : -1) << ","
              << "\"dram_pct\":"      << (dram_pct    >= 0 ? dram_pct    : -1.0)             << ","
              << "\"utilization\":[";
    for (int c = 0; c < numCores; ++c) {
        if (c) std::cout << ",";
        std::cout << util[c];
    }
    std::cout << "]";

    if (has_device_info) {
        std::cout << ","
                  << "\"firmware_version\":\"" << escapeJson(fw_ver) << "\","
                  << "\"device_type\":\""      << escapeJson(dev_type) << "\","
                  << "\"device_variant\":\""   << escapeJson(dev_variant) << "\","
                  << "\"board_type\":\""       << escapeJson(board_type) << "\","
                  << "\"memory_type\":\""      << escapeJson(mem_type) << "\","
                  << "\"memory_size_bytes\":"  << mem_size << ","
                  << "\"memory_freq_mhz\":"   << mem_freq << ","
                  << "\"ddr_status\":["        << ddr_status[0] << "," << ddr_status[1] << "," << ddr_status[2] << "," << ddr_status[3] << "],"
                  << "\"ddr_sbe_cnt\":["       << ddr_sbe[0] << "," << ddr_sbe[1] << "," << ddr_sbe[2] << "," << ddr_sbe[3] << "],"
                  << "\"ddr_dbe_cnt\":["       << ddr_dbe[0] << "," << ddr_dbe[1] << "," << ddr_dbe[2] << "," << ddr_dbe[3] << "]";
    }

    std::cout << "}" << std::endl;
    return 0;
}
