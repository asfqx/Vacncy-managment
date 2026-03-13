import { http } from "./http";

export const usersApi = {
  getMe() {
    return http.get("/api/v1/users/me/").then((r) => r.data);
  },

  updateMe(payload) {
    return http.patch("/api/v1/users/me/", payload).then((r) => r.data);
  },

  getAvatarUploadUrl() {
    return http.get("/api/v1/users/me/avatar/upload-url").then((r) => r.data);
  },
};
