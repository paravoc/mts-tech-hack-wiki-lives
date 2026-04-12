#pragma once

#include <string>
#include <vector>

#include "src/models/comment_thread.h"

namespace wikilive::models {

struct PageVersion {
    std::string versionId;
    std::string pageId;
    std::string title;
    std::string content;
    std::string createdAt;
    std::string label;
    std::string author;
    std::vector<CommentThread> threadSnapshot;
    std::string commentAccessMode;
};

}  // namespace wikilive::models
