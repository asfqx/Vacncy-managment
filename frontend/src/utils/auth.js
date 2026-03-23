export const USER_ROLES = {
  ADMIN: "admin",
  CANDIDATE: "candidate",
  COMPANY: "company",
};

function decodeBase64Url(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), "=");
  return decodeURIComponent(
    atob(padded)
      .split("")
      .map((char) => `%${char.charCodeAt(0).toString(16).padStart(2, "0")}`)
      .join("")
  );
}

export function parseJwtPayload(token) {
  if (!token) return null;

  const parts = token.split(".");
  if (parts.length < 2) return null;

  try {
    return JSON.parse(decodeBase64Url(parts[1]));
  } catch {
    return null;
  }
}

export function normalizeRole(role) {
  return String(role || "").toLowerCase();
}

export function getAccessToken() {
  return localStorage.getItem("access_token");
}

export function getUserRoleFromToken(token = getAccessToken()) {
  return normalizeRole(parseJwtPayload(token)?.role);
}

export function isAdminRole(role) {
  return normalizeRole(role) === USER_ROLES.ADMIN;
}

export function isEmployerRole(role) {
  const normalizedRole = normalizeRole(role);
  return normalizedRole === USER_ROLES.COMPANY || normalizedRole === USER_ROLES.ADMIN;
}

export function isCandidateRole(role) {
  return normalizeRole(role) === USER_ROLES.CANDIDATE;
}

export function getDefaultRouteForRole(role) {
  if (isEmployerRole(role) || isCandidateRole(role)) return "/home";
  return "/login";
}

export function getRoleLabel(role) {
  if (isAdminRole(role)) return "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440";
  if (isEmployerRole(role)) return "\u0420\u0430\u0431\u043e\u0442\u043e\u0434\u0430\u0442\u0435\u043b\u044c";
  if (isCandidateRole(role)) return "\u041a\u0430\u043d\u0434\u0438\u0434\u0430\u0442";
  return "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c";
}