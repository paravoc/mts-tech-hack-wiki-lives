#pragma once

#include <string>
#include <vector>

#include "src/utils/errors.h"
#include "src/wiki/wiki_insert.h"

namespace wikilive::wiki {

class WikiParser {
public:
    [[nodiscard]] utils::Expected<std::vector<WikiInsert>> parse(const std::string& content) const;
};

}  // namespace wikilive::wiki
