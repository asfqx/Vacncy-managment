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

export function isEmployerRole(role) {
  const normalizedRole = normalizeRole(role);
  return normalizedRole === USER_ROLES.COMPANY || normalizedRole === USER_ROLES.ADMIN;
}

export function isCandidateRole(role) {
  return normalizeRole(role) === USER_ROLES.CANDIDATE;
}

export function getDefaultRouteForRole(role) {
  if (isEmployerRole(role)) return "/employer/resumes";
  if (isCandidateRole(role)) return "/vacancies";
  return "/login";
}

export function getRoleLabel(role) {
  if (isEmployerRole(role)) return "Работодатель";
  if (isCandidateRole(role)) return "Кандидат";
  return "Пользователь";
}
