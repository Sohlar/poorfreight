import { format, parseISO } from 'date-fns';

export function formatDate(dateString: string): string {
  try {
    return format(parseISO(dateString), 'MMM d, yyyy');
  } catch {
    return dateString;
  }
}

export function formatDateTime(dateString: string): string {
  try {
    return format(parseISO(dateString), 'MMM d, yyyy h:mm a');
  } catch {
    return dateString;
  }
}

export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return 'N/A';
  return value.toFixed(decimals);
}

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  return `$${value.toFixed(2)}`;
}

export function formatChange(value: number | null | undefined): {
  text: string;
  isPositive: boolean;
  isNegative: boolean;
} {
  if (value === null || value === undefined) {
    return { text: 'N/A', isPositive: false, isNegative: false };
  }

  const sign = value >= 0 ? '+' : '';
  return {
    text: `${sign}${value.toFixed(3)}`,
    isPositive: value > 0,
    isNegative: value < 0
  };
}

export function highlightText(text: string, query: string): string[] {
  if (!query.trim()) return [text];
  return text.split(new RegExp(`(${query})`, 'gi'));
}

export function isHighlightMatch(part: string, query: string): boolean {
  return part.toLowerCase() === query.toLowerCase();
}
