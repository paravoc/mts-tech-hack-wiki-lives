#include "src/utils/string_utils.h"
#include "tests/test_common.h"

namespace {

void decodesBasicJsonEscapes() {
    const auto value = wikilive::utils::unescapeJson(R"(line 1\nline 2\t\"quoted\")");

    wikilive::tests::expectEqual(
        value,
        std::string("line 1\nline 2\t\"quoted\""),
        "unescapeJson should decode common escaped characters");
}

void decodesUnicodeEscapesToUtf8() {
    const auto value = wikilive::utils::unescapeJson(R"(\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435)");

    wikilive::tests::expectEqual(
        value,
        std::string("\xD0\x9D\xD0\xB0\xD0\xB7\xD0\xB2\xD0\xB0\xD0\xBD\xD0\xB8\xD0\xB5"),
        "unescapeJson should decode unicode escapes to utf-8");
}

void decodesSurrogatePairs() {
    const auto value = wikilive::utils::unescapeJson(R"(\ud83d\ude80)");

    wikilive::tests::expectEqual(
        value,
        std::string("\xF0\x9F\x9A\x80"),
        "unescapeJson should decode surrogate pairs");
}

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"decodes basic json escapes", decodesBasicJsonEscapes},
        {"decodes unicode escapes to utf-8", decodesUnicodeEscapesToUtf8},
        {"decodes surrogate pairs", decodesSurrogatePairs},
    });
}
