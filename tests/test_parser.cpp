#include "src/wiki/wiki_parser.h"
#include "tests/test_common.h"

namespace {

void parsesSingleInsert() {
    const wikilive::wiki::WikiParser parser;
    const auto inserts = parser.parse("Status: {{projects:rec123:status}}");

    wikilive::tests::expect(inserts.has_value(), "parser should return inserts");
    wikilive::tests::expectEqual(inserts->size(), static_cast<std::size_t>(1), "single insert should be found");
    wikilive::tests::expectEqual(inserts->front().tableId, std::string("projects"), "tableId should match");
    wikilive::tests::expectEqual(inserts->front().recordId, std::string("rec123"), "recordId should match");
    wikilive::tests::expectEqual(inserts->front().fieldName, std::string("status"), "fieldName should match");
}

void parsesMultipleUnicodeInserts() {
    const wikilive::wiki::WikiParser parser;
    const auto inserts = parser.parse(
        "Статус: {{dst1:rec1:Название}}, KPI: {{dst2:rec2:Выручка}}");

    wikilive::tests::expect(inserts.has_value(), "parser should support unicode content");
    wikilive::tests::expectEqual(inserts->size(), static_cast<std::size_t>(2), "two inserts should be found");
    wikilive::tests::expectEqual(inserts->at(1).fieldName, std::string("Выручка"), "unicode field name should match");
}

void returnsEmptyCollectionForPlainText() {
    const wikilive::wiki::WikiParser parser;
    const auto inserts = parser.parse("No dynamic values here");

    wikilive::tests::expect(inserts.has_value(), "plain text should not fail");
    wikilive::tests::expect(inserts->empty(), "plain text should produce no inserts");
}

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"parses single insert", parsesSingleInsert},
        {"parses multiple unicode inserts", parsesMultipleUnicodeInserts},
        {"returns empty collection for plain text", returnsEmptyCollectionForPlainText},
    });
}
