#include "src/wiki/wiki_renderer.h"

#include <utility>

#include "src/utils/string_utils.h"

namespace wikilive::wiki {

WikiRenderer::WikiRenderer(api::MwsClient* mwsClient)
    : mwsClient_(mwsClient) {
}

utils::Expected<std::string> WikiRenderer::render(const std::string& content) const {
    const auto parsed = parser_.parse(content);
    if (!parsed) {
        return std::unexpected(parsed.error());
    }

    std::string rendered = content;
    for (const auto& insert : parsed.value()) {
        std::string label = insert.fieldName;
        if (mwsClient_ != nullptr) {
            const auto fieldValue = mwsClient_->getFieldValue(insert.tableId, insert.recordId, insert.fieldName);
            if (fieldValue) {
                label = fieldValue->value;
            }
        }

        const auto replacement =
            "<span class=\"wikilive-insert\" data-table=\"" + utils::escapeHtml(insert.tableId) +
            "\" data-record=\"" + utils::escapeHtml(insert.recordId) +
            "\" data-field=\"" + utils::escapeHtml(insert.fieldName) +
            "\">" + utils::escapeHtml(label) + "</span>";

        rendered = utils::replaceAll(std::move(rendered), insert.raw, replacement);
    }

    return rendered;
}

}  // namespace wikilive::wiki
