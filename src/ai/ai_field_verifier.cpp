#include "src/ai/ai_field_verifier.h"

#include "src/api/mws_client.h"

namespace wikilive::ai {

MwsAiFieldVerifier::MwsAiFieldVerifier(api::MwsClient& mwsClient)
    : mwsClient_(mwsClient) {
}

utils::Expected<bool> MwsAiFieldVerifier::exists(
    const std::string& tableId,
    const std::string& recordId,
    const std::string& fieldName) const {
    const auto value = mwsClient_.getFieldValue(tableId, recordId, fieldName);
    if (value) {
        return true;
    }

    const auto& error = value.error();
    if (error.code == utils::ErrorCode::PageNotFound) {
        return false;
    }

    if (error.code == utils::ErrorCode::MwsApiError && error.httpStatus == 404) {
        return false;
    }

    if (error.code == utils::ErrorCode::InvalidRequest) {
        return false;
    }

    return std::unexpected(error);
}

}  // namespace wikilive::ai
