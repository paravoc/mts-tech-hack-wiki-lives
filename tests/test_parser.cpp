#include "src/wiki/wiki_parser.h"

int main() {
    const wikilive::wiki::WikiParser parser;
    const auto inserts = parser.parse("Status: {{projects:rec123:status}}");
    if (!inserts) {
        return 1;
    }

    return inserts->size() == 1 ? 0 : 1;
}
