
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
test_text = "AAGGCGGCTTCA$"
p = "GGC"

sa = suffix_array(test_text)
a, b = find_block(test_text, sa, p)

assert sorted(sa[a:b]) == brute_force(test_text, p)
assert (a, b) == (9, 11)

print("sa:", sa)
print("find_block (a, b):", (a, b))
print("pozice výskytů:", sa[a:b])
print("brute_force:", brute_force(test_text, p))


# TASK 2 - The Burrows-Wheeler transform and its inverse

def bwt(text, sa):
    result = ""
    for idx in sa:
        # Take the letter before the suffix
        result += text[idx - 1]
    return result


def first_occurrence(letters):
    # F column is simply BWT sorted alphabetically
    first = {}
    f_column = sorted(letters)

    # Store the first index where each character appears in F
    for i, char in enumerate(f_column):
        if char not in first:
            first[char] = i

    return first


def inverse_bwt(bwt_str):
    if not bwt_str:
        return ""

    first_occ = first_occurrence(bwt_str)

    # Reconstruct text backwards, ending with '$'
    text = "$"
    row = 0  # start at row 0 where '$' is located in column F

    for _ in range(len(bwt_str) - 1):
        char = bwt_str[row]
        # Prepend the found letter to the growing text
        text = char + text

        # How many times this letter appeared above current row in BWT
        k = bwt_str[:row].count(char)

        # Move to the corresponding row in column F (LF-mapping)
        row = first_occ[char] + k

    return text

def count_runs(s):
    # Count maximal blocks of identical neighbouring letters
    if not s:
        return 0
    runs = 1
    for i in range(1, len(s)):
        if s[i] != s[i - 1]:
            runs += 1
    return runs


# SELF-CHECK
test_text = "AAGGCGGCTTCA$"
test_sa = suffix_array(test_text)
test_bwt = bwt(test_text, test_sa)

# Verify BWT and inverse reconstruction against the handout example
assert test_bwt == "AC$ATGGGGACTC"
assert inverse_bwt(test_bwt) == test_text

print("bwt:", test_bwt)
print("inverse_bwt:", inverse_bwt(test_bwt))
print("first_occurrence:", first_occurrence(test_bwt))



# TASK 3 - The FMIndex class

class FMIndex:
    def __init__(self, text, s):
        self.s = s
        full_sa = suffix_array(text)
        self.bwt = bwt(text, full_sa)
        self.first_occ = first_occurrence(self.bwt)

        # Keep suffix array position only if it is divisible by s
        self.sampled = {}
        for row, pos in enumerate(full_sa):
            if pos % s == 0:
                self.sampled[row] = pos

    def lf(self, row):
        # LF-mapping: move from column L to column F
        char = self.bwt[row]
        k = self.bwt[:row].count(char)
        return self.first_occ[char] + k

    def count(self, p):
        # Backward search for pattern p: interval [top, bottom)
        top = 0
        bottom = len(self.bwt)

        # Read pattern backwards from right to left
        for char in reversed(p):
            if char not in self.first_occ:
                return top, top

            # Update rows using LF logic
            top = self.first_occ[char] + self.bwt[:top].count(char)
            bottom = self.first_occ[char] + self.bwt[:bottom].count(char)

            if top >= bottom:
                return top, top

        return top, bottom

    def locate(self, p):
        # Find start positions of pattern p in the text
        top, bottom = self.count(p)
        if top >= bottom:
            return []

        positions = []
        for row in range(top, bottom):
            curr_row = row
            steps = 0

            # Follow LF steps until we find a sampled position
            while curr_row not in self.sampled:
                curr_row = self.lf(curr_row)
                steps += 1

            positions.append(self.sampled[curr_row] + steps)

        return sorted(positions)


# SELF-CHECK
test_text = "AAGGCGGCTTCA$"
p = "GGC"
fm = FMIndex(test_text, 2)

# Verify count and locate against our results from Task 1
assert fm.count(p) == (9, 11)
assert fm.locate(p) == [2, 5]

print("fm.count('GGC'):", fm.count(p))
print("fm.locate('GGC'):", fm.locate(p))


# TASK 4 - Mapping reads

def count_mismatches(s1, s2):
    # Count how many characters differ between two strings
    mismatches = 0
    for a, b in zip(s1, s2):
        if a != b:
            mismatches += 1
    return mismatches


def query_approximate(fm, text, p, k):
    # Return all start positions in text where p matches with at most k mismatches
    m = len(p)
    n = len(text)
    num_seeds = k + 1
    seed_len = m // num_seeds

    matches = set()

    for i in range(num_seeds):
        # Calculate start and end index for i-th seed piece
        start = i * seed_len
        if i == num_seeds - 1:
            end = m  # last piece takes the rest of the pattern
        else:
            end = (i + 1) * seed_len

        seed = p[start:end]

        # Find exact matches of the seed using FMIndex
        for pos in fm.locate(seed):
            # Candidate start position for the whole pattern in text
            cand_start = pos - start

            # Skip candidates that fall outside text boundaries
            if cand_start < 0 or cand_start + m > n:
                continue

            # Compare the candidate substring with pattern p
            sub = text[cand_start:cand_start + m]
            if count_mismatches(sub, p) <= k:
                matches.add(cand_start)

    return sorted(matches)


# SELF-CHECK
test_text = "AAGGCGGCTTCA$"
fm = FMIndex(test_text, 2)

results = query_approximate(fm, test_text, "GGT", 1)
print("query_approximate('GGT', k=1):", results)

assert results == [2, 5, 6]