import { http } from "./http";

export const authApi = {
  login(payload) {
    return http.post("/api/v1/auth/login", payload).then((r) => r.data);
  },

  register(payload) {
    return http.post("/api/v1/auth/register", payload).then((r) => r.data);
  },

  emailConfirmRequest(email) {
    return http
      .post("/api/v1/auth/email-confirm/request", null, { params: { email } })
      .then((r) => r.data);
  },

  emailConfirmConfirm({ email, token }) {
    return http
      .post("/api/v1/auth/email-confirm/confirm", { email }, { params: { token } })
      .then((r) => r.data);
  },

  passwordResetRequest(email) {
    return http
      .post("/api/v1/auth/password-reset/request", null, {
        params: { email },
      })
      .then((r) => r.data);
  },

  passwordResetConfirm({ email, token, new_password }) {
    return http
      .post(
        "/api/v1/auth/password-reset/confirm",
        { email, new_password },
        { params: { token } }
      )
      .then((r) => r.data);
  },

  logout() {
    return http.post("/api/v1/auth/logout").then((r) => r.data);
  },
};