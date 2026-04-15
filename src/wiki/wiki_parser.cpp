#include "src/wiki/wiki_parser.h"

#include <exception>
#include <regex>
#include <utility>

#include "config/constants.h"

namespace wikilive::wiki {

utils::Expected<std::vector<WikiInsert>> WikiParser::parse(const std::string& content) const {
    try {
        const std::regex pattern{std::string{config::kWikiInsertPattern}};
        std::vector<WikiInsert> inserts;

        for (std::sregex_iterator it(content.begin(), content.end(), pattern), end; it != end; ++it) {
            WikiInsert insert;
            insert.raw = it->str(0);
            insert.tableId = it->str(1);
            insert.recordId = it->str(2);
            insert.fieldName = it->str(3);

            if (insert.tableId.empty() || insert.recordId.empty() || insert.fieldName.empty()) {
                return wikilive::utils::makeUnexpected(utils::makeError(
                    utils::ErrorCode::ParserError,
                    "Wiki insert contains empty parts: " + insert.raw,
                    400,
                    false));
            }

            inserts.push_back(std::move(insert));
        }

        return inserts;
    } catch (const std::regex_error& exception) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::ParserError,
            std::string("Regex parser error: ") + exception.what(),
            400,
            false));
    } catch (const std::exception& exception) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            std::string("Unexpected parser exception: ") + exception.what(),
            500,
            false));
    } catch (...) {
        return wikilive::utils::makeUnexpected(utils::makeError(
            utils::ErrorCode::InternalError,
            "Unknown parser exception",
            500,
            false));
    }
}

}  // namespace wikilive::wiki
