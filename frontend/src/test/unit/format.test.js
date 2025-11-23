import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatDate,
  formatTimeAgo,
  truncate,
  capitalize
} from '../../utils/format';

describe('Format Utilities', () => {
  describe('formatCurrency', () => {
    it('formats numbers as currency', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(0)).toBe('$0.00');
      expect(formatCurrency(1234567.89)).toBe('$1,234,567.89');
    });

    it('handles decimal values', () => {
      expect(formatCurrency(99.99)).toBe('$99.99');
      expect(formatCurrency(0.50)).toBe('$0.50');
    });

    it('handles null and undefined', () => {
      expect(formatCurrency(null)).toBe('$0.00');
      expect(formatCurrency(undefined)).toBe('$0.00');
    });

    it('handles negative numbers', () => {
      expect(formatCurrency(-100)).toBe('-$100.00');
    });
  });

  describe('formatDate', () => {
    it('formats ISO dates', () => {
      const date = '2024-01-15T10:30:00Z';
      const result = formatDate(date);
      expect(result).toContain('2024');
      expect(result).toContain('Jan');
      expect(result).toContain('15');
    });

    it('handles empty string', () => {
      expect(formatDate('')).toBe('');
    });

    it('handles null and undefined', () => {
      expect(formatDate(null)).toBe('');
      expect(formatDate(undefined)).toBe('');
    });
  });

  describe('formatTimeAgo', () => {
    it('returns "just now" for recent dates', () => {
      const now = new Date();
      expect(formatTimeAgo(now.toISOString())).toBe('just now');
    });

    it('returns minutes ago', () => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      expect(formatTimeAgo(fiveMinutesAgo.toISOString())).toBe('5 minutes ago');
    });

    it('returns singular minute for 1 minute', () => {
      const oneMinuteAgo = new Date(Date.now() - 1 * 60 * 1000);
      expect(formatTimeAgo(oneMinuteAgo.toISOString())).toBe('1 minute ago');
    });

    it('returns hours ago', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000);
      expect(formatTimeAgo(twoHoursAgo.toISOString())).toBe('2 hours ago');
    });

    it('returns days ago', () => {
      const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000);
      expect(formatTimeAgo(threeDaysAgo.toISOString())).toBe('3 days ago');
    });

    it('handles empty string', () => {
      expect(formatTimeAgo('')).toBe('');
    });

    it('handles null and undefined', () => {
      expect(formatTimeAgo(null)).toBe('');
      expect(formatTimeAgo(undefined)).toBe('');
    });
  });

  describe('truncate', () => {
    it('truncates long strings', () => {
      const longString = 'This is a very long string that should be truncated to a maximum length';
      const result = truncate(longString, 20);
      expect(result).toBe('This is a very long ...');
      expect(result.length).toBeLessThanOrEqual(23); // 20 + '...'
    });

    it('does not truncate short strings', () => {
      const shortString = 'Short';
      expect(truncate(shortString, 20)).toBe('Short');
    });

    it('handles empty string', () => {
      expect(truncate('')).toBe('');
    });

    it('handles null and undefined', () => {
      expect(truncate(null)).toBe('');
      expect(truncate(undefined)).toBe('');
    });

    it('uses default max length of 100', () => {
      const str = 'a'.repeat(150);
      const result = truncate(str);
      expect(result.length).toBe(103); // 100 + '...'
    });
  });

  describe('capitalize', () => {
    it('capitalizes first letter', () => {
      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('world')).toBe('World');
    });

    it('handles already capitalized strings', () => {
      expect(capitalize('Hello')).toBe('Hello');
    });

    it('handles single character', () => {
      expect(capitalize('a')).toBe('A');
    });

    it('handles empty string', () => {
      expect(capitalize('')).toBe('');
    });

    it('handles null and undefined', () => {
      expect(capitalize(null)).toBe('');
      expect(capitalize(undefined)).toBe('');
    });
  });
});
