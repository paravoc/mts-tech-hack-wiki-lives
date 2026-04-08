#pragma once

#include "src/core/app_config.h"

namespace wikilive::core {

class Application {
public:
    Application() = default;

    bool initialize(const char* envPath = ".env");
    int run();
    void stop();

    [[nodiscard]] const AppConfig& config() const;

private:
    AppConfig config_{};
    bool initialized_ = false;
};

}  // namespace wikilive::core
