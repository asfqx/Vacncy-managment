import { http } from "./http";

export const responsesApi = {
  generate(payload) {
    return http.post("/api/v1/responses/generate", payload).then((r) => r.data);
  },

  create(payload) {
    return http.post("/api/v1/responses/", payload).then((r) => r.data);
  },

  getAll() {
    return http.get("/api/v1/responses/").then((r) => r.data);
  },

  getById(uuid) {
    return http.get(`/api/v1/responses/${uuid}`).then((r) => r.data);
  },

  updateStatus(uuid, payload) {
    return http.patch(`/api/v1/responses/${uuid}/status`, payload).then((r) => r.data);
  },

  delete(uuid) {
    return http.delete(`/api/v1/responses/${uuid}`).then((r) => r.data);
  },
};
