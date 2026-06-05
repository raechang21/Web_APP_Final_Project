export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function clampPercent(score: number, max = 6) {
  return Math.max(0, Math.min(100, (score / max) * 100));
}

export function formatDate(iso?: string | null) {
  if (!iso) {
    return "尚未建立";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return new Intl.DateTimeFormat("zh-TW", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Taipei",
  }).format(date);
}
