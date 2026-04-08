#include "src/core/application.h"

#include <exception>
#include <iostream>

int main() {
    try {
        wikilive::core::Application app;
        if (!app.initialize()) {
            return 1;
        }

        return app.run();
    } catch (const std::exception& exception) {
        std::cerr << "Fatal error: " << exception.what() << '\n';
        return 1;
    } catch (...) {
        std::cerr << "Fatal error: unknown exception\n";
        return 1;
    }
}
