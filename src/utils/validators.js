/**
 * Validation rules for React Hook Form or manual validation
 */
export const emailPattern = {
  value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  message: 'Enter a valid email address',
};

export const phonePattern = {
  value: /^[6-9]\d{9}$/,
  message: 'Enter a valid 10-digit Indian phone number',
};

export const pinCodePattern = {
  value: /^\d{6}$/,
  message: 'Enter a valid 6-digit Indian PIN code',
};
