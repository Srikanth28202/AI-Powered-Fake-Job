// src/utils/cn.js
// Utility: merge Tailwind class names conditionally
import { clsx } from 'clsx'

export function cn(...inputs) {
  return clsx(inputs)
}
