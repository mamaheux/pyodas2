#include <sstream>

#include <odas2/utils/error.h>

#include "error.h"

std::string pyodas2_error_message() {
    std::string message = odas2_error_message();

    auto colon_index = message.find(':');
    if (colon_index != std::string::npos) {
        message = message.substr(colon_index + 1);
    }

    message.erase(0, message.find_first_not_of(" \t\n\r\f\v"));

    if (!message.empty()) {
        message[0] = toupper(message[0]);
    }

    return message;
}
