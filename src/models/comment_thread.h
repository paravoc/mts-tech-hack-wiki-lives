#pragma once

#include <string>
#include <vector>

namespace wikilive::models {

struct CommentMessage {
    std::string messageId;
    std::string author;
    std::string body;
    std::string createdAt;
    std::string updatedAt;
    std::string replyToMessageId;
    bool deleted = false;
    std::vector<std::string> likedBy;
};

struct CommentThread {
    std::string threadId;
    std::string pageId;
    std::string targetId;
    std::string targetType;
    std::string selectionLabel;
    std::string targetPreview;
    std::string createdAt;
    std::string updatedAt;
    bool resolved = false;
    std::string resolvedAt;
    std::string resolvedBy;
    bool deleted = false;
    std::string deletedAt;
    std::string deletedBy;
    std::vector<std::string> likedBy;
    std::vector<CommentMessage> messages;
};

}  // namespace wikilive::models
