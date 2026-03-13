import { http } from "./http";

export const vacanciesApi = {
  getRecommendations({ limit = 10 } = {}) {
    return http
      .get("/api/v1/vacancies/recommendation", { params: { limit } })
      .then((r) => r.data);
  },

  getAll(params) {
    return http.get("/api/v1/vacancies", { params }).then((r) => r.data);
  },

  search(params) {
    return http.get("/api/v1/vacancies/search", { params }).then((r) => r.data);
  },

  getById(uuid) {
    return http.get(`/api/v1/vacancies/${uuid}`).then((r) => r.data);
  },

  create(payload) {
    return http.post("/api/v1/vacancies/", payload).then((r) => r.data);
  },

  delete(uuid) {
    return http.delete(`/api/v1/vacancies/${uuid}`).then((r) => r.data);
  },
};
