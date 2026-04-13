#pragma once

#include <cstddef>
#include <string>
#include <vector>

#include "src/models/comment_thread.h"

namespace wikilive::models {

struct PageVersion {
    std::string versionId;
    std::string pageId;
    std::string title;
    std::string description;
    std::string content;
    std::string createdAt;
    std::string label;
    std::string author;
    std::vector<std::string> sharedWith;
    std::vector<CommentThread> threadSnapshot;
    std::string commentAccessMode;
    std::size_t threadCount = 0;
    std::size_t commentCount = 0;
};

}  // namespace wikilive::models
