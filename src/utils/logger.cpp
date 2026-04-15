#include "src/utils/logger.h"

#include <iostream>

namespace wikilive::utils {

Logger& Logger::instance() {
    static Logger logger;
    return logger;
}

void Logger::setLevel(const std::string& level) {
    level_ = level;
}

void Logger::info(const std::string& message) const {
    std::cout << "[INFO] " << message << '\n';
}

void Logger::warn(const std::string& message) const {
    std::cout << "[WARN] " << message << '\n';
}

void Logger::error(const std::string& message) const {
    std::cerr << "[ERROR] " << message << '\n';
}

}  // namespace wikilive::utils
