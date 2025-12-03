from rapidfuzz import fuzz

def fuzzy_match(str1, str2):
    return fuzz.token_sort_ratio(str1, str2)

