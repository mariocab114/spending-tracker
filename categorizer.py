CATEGORY_KEYWORDS = {
    "Food & Dining": ["starbucks", "mcdonald", "chipotle", "doordash", "whole foods"],
    "Transportation": ["uber", "lyft", "shell", "exxon", "gas station"],
    "Shopping": ["amazon", "target"],
    "Bills & Utilities": ["electric", "con edison", "netflix", "subscription"],
}

def categorize(description):
    description = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                return category
    return "Uncategorized"