import { http } from "./http";

export const companyApi = {
  getMine() {
    return http.get("/api/v1/companies/me/").then((r) => r.data);
  },

  getByUserId(userUuid) {
    return http.get(`/api/v1/companies/by-user/${userUuid}/`).then((r) => r.data);
  },

  getById(uuid) {
    return http.get(`/api/v1/companies/${uuid}/`).then((r) => r.data);
  },

  createMine(payload) {
    return http.post("/api/v1/companies/me/", payload).then((r) => r.data);
  },

  updateMine(payload) {
    return http.patch("/api/v1/companies/me/", payload).then((r) => r.data);
  },
};
