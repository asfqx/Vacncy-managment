import { http } from "./http";

export const usersApi = {
  getAll(params) {
    return http.get("/api/v1/users/", { params }).then((r) => r.data);
  },

  getMe() {
    return http.get("/api/v1/users/me/").then((r) => r.data);
  },

  getById(uuid) {
    return http.get(`/api/v1/users/${uuid}`).then((r) => r.data);
  },

  updateMe(payload) {
    return http.patch("/api/v1/users/me/", payload).then((r) => r.data);
  },

  delete(uuid) {
    return http.delete(`/api/v1/users/${uuid}`).then((r) => r.data);
  },

  unban(uuid) {
    return http.patch(`/api/v1/users/${uuid}/unban`).then((r) => r.data);
  },

  getAvatarUploadUrl() {
    return http.get("/api/v1/users/me/avatar/upload-url").then((r) => r.data);
  },
};
