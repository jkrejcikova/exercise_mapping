
# TASK 1 - Suffix array and binary search

def brute_force(text, p):
    # If the pattern is empty, there is nothing to match
    if not p:
        return []

    res = []
    n, m = len(text), len(p)

    # Check every possible start position in the text
    for i in range(n - m + 1):
        # If the substring matches the pattern, save the start index
        if text[i:i + m] == p:
            res.append(i)
    return res

def suffix_array(text):
    # Sort all start indices by their suffixes in alphabetical order
    sa = sorted(range(len(text)), key=lambda i: text[i:])
    return sa

def find_block(text, sa, p):
    m = len(p)
    n = len(sa)

    # First binary search → find first row where prefix >= p
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        # Compare only the first m letters of the suffix with p
        if text[sa[mid]:sa[mid] + m] < p:
            lo = mid + 1
        else:
            hi = mid
    a = lo

    # Second binary search → find first row where prefix > p
    lo, hi = a, n
    while lo < hi:
        mid = (lo + hi) // 2
        # Move right as long as the prefix is <= p
        if text[sa[mid]:sa[mid] + m] <= p:
            lo = mid + 1
        else:
            hi = mid
    b = lo

    # Return the half-open interval [a, b) of matching rows
    return a, b


# SELF-CHECK
# Compute suffix array for toy text "CAT$"
sa = suffix_array("CAT$")
assert sa == [3, 1, 0, 2] and find_block("CAT$", sa, "A") == (1, 2)
sa = suffix_array("CAT$")
print("sa:", sa)
print("find_block:", find_block("CAT$", sa, "A"))