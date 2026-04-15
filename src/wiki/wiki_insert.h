#pragma once

#include <string>

namespace wikilive::wiki {

struct WikiInsert {
    std::string raw;
    std::string tableId;
    std::string recordId;
    std::string fieldName;
};

}  // namespace wikilive::wiki
