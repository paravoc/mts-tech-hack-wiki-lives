#pragma once

#include <string>

namespace wikilive::utils {

class Logger {
public:
    static Logger& instance();

    void setLevel(const std::string& level);
    void info(const std::string& message) const;
    void warn(const std::string& message) const;
    void error(const std::string& message) const;

private:
    std::string level_ = "info";
};

}  // namespace wikilive::utils
