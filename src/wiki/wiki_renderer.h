#pragma once

#include <string>

#include "src/utils/errors.h"
#include "src/wiki/wiki_parser.h"

namespace wikilive::wiki {

class WikiRenderer {
public:
    [[nodiscard]] utils::Expected<std::string> render(const std::string& content) const;

private:
    WikiParser parser_{};
};

}  // namespace wikilive::wiki
