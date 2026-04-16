package com.testforge;

import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * TestForge — Java module
 * JUnit 5 tests for a StringUtils utility class.
 * Demonstrates: parameterized tests, nested classes, exception testing.
 */
@DisplayName("StringUtils Test Suite")
class StringUtilsTest {

    // ── class under test (inline) ──────────────────────────────

    static class StringUtils {
        static String reverse(String s) {
            if (s == null) throw new IllegalArgumentException("Input cannot be null");
            return new StringBuilder(s).reverse().toString();
        }

        static boolean isPalindrome(String s) {
            if (s == null) return false;
            String clean = s.toLowerCase().replaceAll("[^a-z0-9]", "");
            return clean.equals(new StringBuilder(clean).reverse().toString());
        }

        static int countVowels(String s) {
            if (s == null) return 0;
            return (int) s.toLowerCase().chars()
                          .filter(c -> "aeiou".indexOf(c) >= 0)
                          .count();
        }

        static String titleCase(String s) {
            if (s == null || s.isBlank()) return s;
            String[] words = s.trim().split("\\s+");
            StringBuilder sb = new StringBuilder();
            for (String w : words) {
                sb.append(Character.toUpperCase(w.charAt(0)))
                  .append(w.substring(1).toLowerCase())
                  .append(" ");
            }
            return sb.toString().trim();
        }

        static boolean isAnagram(String a, String b) {
            if (a == null || b == null) return false;
            char[] ca = a.toLowerCase().toCharArray();
            char[] cb = b.toLowerCase().toCharArray();
            java.util.Arrays.sort(ca);
            java.util.Arrays.sort(cb);
            return java.util.Arrays.equals(ca, cb);
        }
    }

    // ── reverse ───────────────────────────────────────────────

    @Nested
    @DisplayName("reverse()")
    class ReverseTests {

        @Test
        @DisplayName("reverses a simple string")
        void reverseSimple() {
            assertEquals("olleh", StringUtils.reverse("hello"));
        }

        @Test
        @DisplayName("handles single character")
        void reverseSingleChar() {
            assertEquals("a", StringUtils.reverse("a"));
        }

        @Test
        @DisplayName("handles empty string")
        void reverseEmpty() {
            assertEquals("", StringUtils.reverse(""));
        }

        @Test
        @DisplayName("throws on null input")
        void reverseNull() {
            assertThrows(IllegalArgumentException.class,
                () -> StringUtils.reverse(null));
        }

        @ParameterizedTest(name = "reverse({0}) = {1}")
        @CsvSource({"hello,olleh", "racecar,racecar", "abc,cba", "12345,54321"})
        void reverseParameterized(String input, String expected) {
            assertEquals(expected, StringUtils.reverse(input));
        }
    }

    // ── isPalindrome ──────────────────────────────────────────

    @Nested
    @DisplayName("isPalindrome()")
    class PalindromeTests {

        @ParameterizedTest(name = "''{0}'' is a palindrome")
        @ValueSource(strings = {"racecar", "level", "madam", "A man a plan a canal Panama"})
        void validPalindromes(String s) {
            assertTrue(StringUtils.isPalindrome(s));
        }

        @ParameterizedTest(name = "''{0}'' is not a palindrome")
        @ValueSource(strings = {"hello", "world", "java", "testing"})
        void invalidPalindromes(String s) {
            assertFalse(StringUtils.isPalindrome(s));
        }

        @Test
        @DisplayName("null returns false")
        void nullIsFalse() {
            assertFalse(StringUtils.isPalindrome(null));
        }
    }

    // ── countVowels ───────────────────────────────────────────

    @Nested
    @DisplayName("countVowels()")
    class VowelTests {

        @ParameterizedTest(name = "''{0}'' has {1} vowels")
        @CsvSource({"hello,2", "aeiou,5", "rhythm,0", "Programming,3"})
        void countVowelsParametrized(String input, int expected) {
            assertEquals(expected, StringUtils.countVowels(input));
        }

        @Test
        void nullReturnsZero() {
            assertEquals(0, StringUtils.countVowels(null));
        }
    }

    // ── titleCase ─────────────────────────────────────────────

    @Nested
    @DisplayName("titleCase()")
    class TitleCaseTests {

        @Test
        void basicTitleCase() {
            assertEquals("Hello World", StringUtils.titleCase("hello world"));
        }

        @Test
        void alreadyTitleCase() {
            assertEquals("Hello World", StringUtils.titleCase("Hello World"));
        }

        @Test
        void allCaps() {
            assertEquals("Hello World", StringUtils.titleCase("HELLO WORLD"));
        }
    }

    // ── isAnagram ────────────────────────────────────────────

    @Nested
    @DisplayName("isAnagram()")
    class AnagramTests {

        @Test
        void validAnagram() {
            assertTrue(StringUtils.isAnagram("listen", "silent"));
        }

        @Test
        void notAnAnagram() {
            assertFalse(StringUtils.isAnagram("hello", "world"));
        }

        @Test
        void caseInsensitive() {
            assertTrue(StringUtils.isAnagram("Triangle", "Integral"));
        }
    }
}

