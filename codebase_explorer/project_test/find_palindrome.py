def find_palindromes(s: str) -> list:
    """
    Find all distinct palindromic substrings in the given string.

    Args:
        s (str): Input string to search for palindromes.

    Returns:
        list: A list of all distinct palindromic substrings.
    """

    def is_palindrome(substring: str) -> bool:
        return substring == substring[::-1]

    n = len(s)
    palindromes = set()

    for i in range(n):
        # Odd-length palindromes (centered at i)
        l, r = i, i
        while l >= 0 and r < n and s[l] == s[r]:
            palindromes.add(s[l : r + 1])
            l -= 1
            r += 1

        # Even-length palindromes (centered between i and i+1)
        l, r = i, i + 1
        while l >= 0 and r < n and s[l] == s[r]:
            palindromes.add(s[l : r + 1])
            l -= 1
            r += 1

    return sorted(palindromes)


# Example usage:
input_string = "ababa"
print(find_palindromes(input_string))
