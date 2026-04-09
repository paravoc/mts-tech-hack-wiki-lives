#include "src/wiki/wiki_renderer.h"

#include <utility>

#include "src/utils/logger.h"
#include "src/utils/string_utils.h"

namespace wikilive::wiki {

namespace {

std::string renderResolvedField(const WikiInsert& insert, const api::MwsFieldValue& fieldValue) {
    const auto tableAttr = utils::escapeHtml(insert.tableId);
    const auto recordAttr = utils::escapeHtml(insert.recordId);
    const auto fieldAttr = utils::escapeHtml(insert.fieldName);
    const auto label = utils::escapeHtml(fieldValue.value.empty() ? insert.fieldName : fieldValue.value);

    if (!fieldValue.resourceUrl.empty()) {
        const auto resourceUrl = utils::escapeHtml(fieldValue.resourceUrl);
        if (fieldValue.isImage) {
            return
                "<figure class=\"wikilive-attachment wikilive-attachment-image\" data-table=\"" + tableAttr +
                "\" data-record=\"" + recordAttr +
                "\" data-field=\"" + fieldAttr + "\">"
                "<img class=\"wikilive-attachment-image__img\" src=\"" + resourceUrl + "\" alt=\"" + label + "\" />"
                "<figcaption class=\"wikilive-attachment-image__caption\">" + label + "</figcaption>"
                "</figure>";
        }

        return
            "<a class=\"wikilive-insert wikilive-insert-link\" data-table=\"" + tableAttr +
            "\" data-record=\"" + recordAttr +
            "\" data-field=\"" + fieldAttr +
            "\" href=\"" + resourceUrl + "\" target=\"_blank\" rel=\"noreferrer\">" + label + "</a>";
    }

    return
        "<span class=\"wikilive-insert\" data-table=\"" + tableAttr +
        "\" data-record=\"" + recordAttr +
        "\" data-field=\"" + fieldAttr +
        "\">" + label + "</span>";
}

}  // namespace

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
        std::string replacement;
        if (mwsClient_ != nullptr) {
            const auto fieldValue = mwsClient_->getFieldValue(insert.tableId, insert.recordId, insert.fieldName);
            if (fieldValue) {
                label = fieldValue->value;
                replacement = renderResolvedField(insert, fieldValue.value());
            } else {
                utils::Logger::instance().warn(
                    "Could not resolve wiki insert " + insert.raw + ": " + fieldValue.error().message);
            }
        }

        if (replacement.empty()) {
            replacement =
                "<span class=\"wikilive-insert\" data-table=\"" + utils::escapeHtml(insert.tableId) +
                "\" data-record=\"" + utils::escapeHtml(insert.recordId) +
                "\" data-field=\"" + utils::escapeHtml(insert.fieldName) +
                "\">" + utils::escapeHtml(label) + "</span>";
        }

        rendered = utils::replaceAll(std::move(rendered), insert.raw, replacement);
    }

    return rendered;
}

}  // namespace wikilive::wiki
