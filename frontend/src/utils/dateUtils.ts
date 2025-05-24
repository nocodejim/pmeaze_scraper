export function formatTimestamp(date: Date): string {
  if (!(date instanceof Date) || isNaN(date.getTime())) {
    return 'Invalid date';
  }

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  const inputDateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  const hours = date.getHours();
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const formattedHours = (hours % 12 || 12).toString(); // Convert 0 to 12 for 12 AM/PM

  if (inputDateOnly.getTime() === today.getTime()) {
    return `${formattedHours}:${minutes} ${ampm}`; // e.g., "10:30 AM"
  } else if (inputDateOnly.getTime() === yesterday.getTime()) {
    return `Yesterday at ${formattedHours}:${minutes} ${ampm}`; // e.g., "Yesterday at 10:30 AM"
  } else {
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${month}/${day}/${year}, ${formattedHours}:${minutes} ${ampm}`; // e.g., "05/23/2024, 10:30 AM"
  }
}
