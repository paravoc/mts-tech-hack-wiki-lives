#pragma once

#include <string>

#include "src/api/mws_client.h"
#include "src/utils/errors.h"
#include "src/wiki/wiki_parser.h"

namespace wikilive::wiki {

class WikiRenderer {
public:
    explicit WikiRenderer(api::MwsClient* mwsClient = nullptr);

    [[nodiscard]] utils::Expected<std::string> render(const std::string& content) const;

private:
    WikiParser parser_{};
    api::MwsClient* mwsClient_ = nullptr;
};

}  // namespace wikilive::wiki
