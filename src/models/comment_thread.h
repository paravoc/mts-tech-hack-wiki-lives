#pragma once

#include <string>
#include <vector>

namespace wikilive::models {

struct CommentMessage {
    std::string messageId;
    std::string author;
    std::string body;
    std::string createdAt;
};

struct CommentThread {
    std::string threadId;
    std::string pageId;
    std::string selectionLabel;
    std::string createdAt;
    std::string updatedAt;
    bool resolved = false;
    std::vector<std::string> likedBy;
    std::vector<CommentMessage> messages;
};

}  // namespace wikilive::models
