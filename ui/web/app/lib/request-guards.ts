const windowMs = 60_000;
const maxHits = 60;

type HitEntry = {
  count: number;
  windowStart: number;
};

const rateStore = new Map<string, HitEntry>();

function nowMs() {
  return Date.now();
}

export function enforceRateLimit(key: string): boolean {
  const current = nowMs();
  const existing = rateStore.get(key);
  if (!existing || current - existing.windowStart > windowMs) {
    rateStore.set(key, { count: 1, windowStart: current });
    return true;
  }
  if (existing.count >= maxHits) {
    return false;
  }
  existing.count += 1;
  rateStore.set(key, existing);
  return true;
}

export function validateOrigin(request: Request): boolean {
  const origin = request.headers.get("origin");
  if (!origin) {
    return true;
  }

  const allowed = process.env.UI_ALLOWED_ORIGINS ?? "https://localhost:18443";
  const allowlist = allowed
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return allowlist.includes(origin);
}

export function isJsonContentType(request: Request): boolean {
  const contentType = request.headers.get("content-type") ?? "";
  return contentType.toLowerCase().includes("application/json");
}

export function clientAddressKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  if (forwarded) {
    return forwarded.split(",")[0]?.trim() ?? "unknown";
  }
  return request.headers.get("x-real-ip") ?? "unknown";
}
