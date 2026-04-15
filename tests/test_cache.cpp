#include "src/storage/cache.h"
#include "tests/test_common.h"

namespace {

void storesAndReturnsValue() {
    wikilive::storage::Cache cache;
    cache.put("demo", "value");

    const auto cached = cache.get("demo");
    wikilive::tests::expect(cached.has_value(), "cache should return stored value");
    wikilive::tests::expectEqual(cached.value(), std::string("value"), "cache value should match");
}

void overwritesExistingValue() {
    wikilive::storage::Cache cache;
    cache.put("demo", "old");
    cache.put("demo", "new");

    const auto cached = cache.get("demo");
    wikilive::tests::expect(cached.has_value(), "cache should keep updated value");
    wikilive::tests::expectEqual(cached.value(), std::string("new"), "cache should overwrite value");
}

void invalidatesValue() {
    wikilive::storage::Cache cache;
    cache.put("demo", "value");
    cache.invalidate("demo");

    wikilive::tests::expect(!cache.get("demo").has_value(), "cache invalidate should remove entry");
}

}  // namespace

int main() {
    return wikilive::tests::runAll({
        {"stores and returns value", storesAndReturnsValue},
        {"overwrites existing value", overwritesExistingValue},
        {"invalidates value", invalidatesValue},
    });
}
