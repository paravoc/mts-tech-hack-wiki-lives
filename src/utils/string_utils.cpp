#include "src/utils/string_utils.h"

#include <cstdint>
#include <sstream>
#include <utility>

namespace {

int hexDigitValue(const char ch) {
    if (ch >= '0' && ch <= '9') {
        return ch - '0';
    }
    if (ch >= 'a' && ch <= 'f') {
        return 10 + (ch - 'a');
    }
    if (ch >= 'A' && ch <= 'F') {
        return 10 + (ch - 'A');
    }
    return -1;
}

bool tryParseHexCodeUnit(const std::string& value, const std::size_t offset, std::uint16_t& codeUnit) {
    if (offset + 4 > value.size()) {
        return false;
    }

    codeUnit = 0;
    for (std::size_t index = 0; index < 4; ++index) {
        const auto digit = hexDigitValue(value[offset + index]);
        if (digit < 0) {
            return false;
        }

        codeUnit = static_cast<std::uint16_t>((codeUnit << 4) | static_cast<std::uint16_t>(digit));
    }

    return true;
}

void appendUtf8(std::string& result, std::uint32_t codePoint) {
    if (codePoint <= 0x7F) {
        result.push_back(static_cast<char>(codePoint));
        return;
    }

    if (codePoint <= 0x7FF) {
        result.push_back(static_cast<char>(0xC0 | ((codePoint >> 6) & 0x1F)));
        result.push_back(static_cast<char>(0x80 | (codePoint & 0x3F)));
        return;
    }

    if (codePoint <= 0xFFFF) {
        result.push_back(static_cast<char>(0xE0 | ((codePoint >> 12) & 0x0F)));
        result.push_back(static_cast<char>(0x80 | ((codePoint >> 6) & 0x3F)));
        result.push_back(static_cast<char>(0x80 | (codePoint & 0x3F)));
        return;
    }

    result.push_back(static_cast<char>(0xF0 | ((codePoint >> 18) & 0x07)));
    result.push_back(static_cast<char>(0x80 | ((codePoint >> 12) & 0x3F)));
    result.push_back(static_cast<char>(0x80 | ((codePoint >> 6) & 0x3F)));
    result.push_back(static_cast<char>(0x80 | (codePoint & 0x3F)));
}

}  // namespace

namespace wikilive::utils {

std::string trim(const std::string& value) {
    const auto start = value.find_first_not_of(" \t\r\n");
    if (start == std::string::npos) {
        return "";
    }

    const auto end = value.find_last_not_of(" \t\r\n");
    return value.substr(start, end - start + 1);
}

std::vector<std::string> split(const std::string& value, const char delimiter) {
    std::stringstream stream(value);
    std::vector<std::string> parts;
    std::string item;

    while (std::getline(stream, item, delimiter)) {
        parts.push_back(item);
    }

    return parts;
}

std::string replaceAll(std::string value, const std::string& from, const std::string& to) {
    if (from.empty()) {
        return value;
    }

    std::size_t pos = 0;
    while ((pos = value.find(from, pos)) != std::string::npos) {
        value.replace(pos, from.size(), to);
        pos += to.size();
    }

    return value;
}

std::string stripQuotes(const std::string& value) {
    if (value.size() >= 2) {
        const bool quotedWithDouble = value.front() == '"' && value.back() == '"';
        const bool quotedWithSingle = value.front() == '\'' && value.back() == '\'';
        if (quotedWithDouble || quotedWithSingle) {
            return value.substr(1, value.size() - 2);
        }
    }

    return value;
}

std::string escapeJson(const std::string& value) {
    std::string escaped;
    escaped.reserve(value.size());

    for (const char ch : value) {
        switch (ch) {
            case '\\':
                escaped += "\\\\";
                break;
            case '"':
                escaped += "\\\"";
                break;
            case '\n':
                escaped += "\\n";
                break;
            case '\r':
                escaped += "\\r";
                break;
            case '\t':
                escaped += "\\t";
                break;
            default:
                escaped += ch;
                break;
        }
    }

    return escaped;
}

std::string unescapeJson(const std::string& value) {
    std::string result;
    result.reserve(value.size());

    bool escape = false;
    for (std::size_t index = 0; index < value.size(); ++index) {
        const char ch = value[index];
        if (escape) {
            switch (ch) {
                case '\\':
                    result.push_back('\\');
                    break;
                case '"':
                    result.push_back('"');
                    break;
                case 'n':
                    result.push_back('\n');
                    break;
                case 'r':
                    result.push_back('\r');
                    break;
                case 't':
                    result.push_back('\t');
                    break;
                case 'u': {
                    std::uint16_t firstCodeUnit = 0;
                    if (!tryParseHexCodeUnit(value, index + 1, firstCodeUnit)) {
                        result.push_back('?');
                        break;
                    }

                    index += 4;

                    if (firstCodeUnit >= 0xD800 && firstCodeUnit <= 0xDBFF) {
                        if (index + 6 < value.size() && value[index + 1] == '\\' && value[index + 2] == 'u') {
                            std::uint16_t secondCodeUnit = 0;
                            if (tryParseHexCodeUnit(value, index + 3, secondCodeUnit) &&
                                secondCodeUnit >= 0xDC00 && secondCodeUnit <= 0xDFFF) {
                                const auto high = static_cast<std::uint32_t>(firstCodeUnit - 0xD800);
                                const auto low = static_cast<std::uint32_t>(secondCodeUnit - 0xDC00);
                                const auto codePoint = 0x10000u + ((high << 10) | low);
                                appendUtf8(result, codePoint);
                                index += 6;
                                break;
                            }
                        }

                        result.push_back('?');
                        break;
                    }

                    if (firstCodeUnit >= 0xDC00 && firstCodeUnit <= 0xDFFF) {
                        result.push_back('?');
                        break;
                    }

                    appendUtf8(result, firstCodeUnit);
                    break;
                }
                default:
                    result.push_back(ch);
                    break;
            }
            escape = false;
            continue;
        }

        if (ch == '\\') {
            escape = true;
            continue;
        }

        result.push_back(ch);
    }

    if (escape) {
        result.push_back('\\');
    }

    return result;
}

std::string escapeHtml(const std::string& value) {
    std::string escaped = value;
    escaped = replaceAll(std::move(escaped), "&", "&amp;");
    escaped = replaceAll(std::move(escaped), "<", "&lt;");
    escaped = replaceAll(std::move(escaped), ">", "&gt;");
    escaped = replaceAll(std::move(escaped), "\"", "&quot;");
    escaped = replaceAll(std::move(escaped), "'", "&#39;");
    return escaped;
}

}  // namespace wikilive::utils
