#include <cctype>
#include <iostream>
#include <string>
#include <vector>

namespace guardrail {

// Converts text into lightweight byte-level token IDs (0..255)
std::vector<int> tokenize_text(const std::string& text) {
    std::vector<int> tokens;
    tokens.reserve(text.size());

    for (unsigned char ch : text) {
        if (!std::isspace(ch)) {
            tokens.push_back(static_cast<int>(ch));
        }
    }

    if (tokens.empty()) {
        tokens.push_back(0);
    }
    return tokens;
}

}  // namespace guardrail

#ifdef STANDALONE_TOKENIZER_MAIN
int main() {
    std::string sample = "Hello [REDACTED], fast C++17 tokenizer";
    std::vector<int> ids = guardrail::tokenize_text(sample);

    std::cout << "Token count: " << ids.size() << "\nTokens: ";
    for (size_t i = 0; i < ids.size(); ++i) {
        std::cout << ids[i] << (i + 1 < ids.size() ? ", " : "");
    }
    std::cout << "\n";
    return 0;
}
#endif