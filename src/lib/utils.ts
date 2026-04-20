/**
 * TigerEx Frontend - Utils
 * @file utils.ts
 * @description Utility functions
 * @author TigerEx Development Team
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
