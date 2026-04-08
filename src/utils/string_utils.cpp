#include "src/utils/string_utils.h"

#include <sstream>
#include <utility>

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
    for (const char ch : value) {
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
