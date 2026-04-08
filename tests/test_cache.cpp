#include "src/storage/cache.h"

int main() {
    wikilive::storage::Cache cache;
    cache.put("demo", "value");
    return cache.get("demo").has_value() ? 0 : 1;
}
