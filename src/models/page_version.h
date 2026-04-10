#pragma once

#include <string>

namespace wikilive::models {

struct PageVersion {
    std::string versionId;
    std::string pageId;
    std::string title;
    std::string content;
    std::string createdAt;
    std::string label;
    std::string author;
};

}  // namespace wikilive::models
