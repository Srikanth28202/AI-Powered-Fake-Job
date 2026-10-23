// src/utils/formatters.js
// Shared formatting helpers

/**
 * Format a decimal probability (0-1) as a percentage string.
 * @param {number} value
 * @param {number} [decimals=1]
 * @returns {string}
 */
export function formatPercent(value, decimals = 1) {
  return `${(value * 100).toFixed(decimals)}%`
}

/**
 * Truncate a string to a max length with ellipsis.
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 100) {
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength)}…` : text
}

/**
 * Format a date string to a human-readable format.
 * @param {string|Date} date
 * @returns {string}
 */
export function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Map a risk score (0-1) to a semantic label.
 * @param {number} score
 * @returns {'low'|'medium'|'high'}
 */
export function riskLabel(score) {
  if (score >= 0.75) return 'high'
  if (score >= 0.4) return 'medium'
  return 'low'
}
