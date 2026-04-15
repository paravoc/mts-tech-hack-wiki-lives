#include "src/utils/time_utils.h"

#include <ctime>
#include <iomanip>
#include <sstream>
#include <thread>

namespace wikilive::utils {

std::chrono::system_clock::time_point now() {
    return std::chrono::system_clock::now();
}

std::string formatIso(const std::chrono::system_clock::time_point timePoint) {
    const auto time = std::chrono::system_clock::to_time_t(timePoint);
    std::tm utcTime{};
#if defined(_WIN32)
    gmtime_s(&utcTime, &time);
#else
    gmtime_r(&time, &utcTime);
#endif

    std::ostringstream stream;
    stream << std::put_time(&utcTime, "%Y-%m-%dT%H:%M:%SZ");
    return stream.str();
}

void sleepMs(const int milliseconds) {
    std::this_thread::sleep_for(std::chrono::milliseconds(milliseconds));
}

}  // namespace wikilive::utils
