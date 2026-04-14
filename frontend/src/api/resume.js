import { http } from "./http";

export const resumeApi = {
  getMine() {
    return http.get("/api/v1/resumes/me").then((r) => r.data);
  },

  getById(uuid) {
    return http.get(`/api/v1/resumes/${uuid}`).then((r) => r.data);
  },

  getAll(params) {
    return http.get("/api/v1/resumes/", { params }).then((r) => r.data);
  },

  search(params) {
    return http.get("/api/v1/resumes/search", { params }).then((r) => r.data);
  },

  getRecommendations({ limit = 10, cursor, cursor_uuid } = {}) {
    return http
      .get("/api/v1/resumes/recommendation", { params: { limit, cursor, cursor_uuid } })
      .then((r) => r.data);
  },

  upsertMine(payload) {
    return http.post("/api/v1/resumes", payload).then((r) => r.data);
  },

  delete(uuid) {
    return http.delete(`/api/v1/resumes/${uuid}`).then((r) => r.data);
  },

  createEducation(resumeUuid, payload) {
    return http.post(`/api/v1/resumes/${resumeUuid}/educations`, payload).then((r) => r.data);
  },

  deleteEducation(resumeUuid, educationUuid) {
    return http.delete(`/api/v1/resumes/${resumeUuid}/educations/${educationUuid}`).then((r) => r.data);
  },

  createExperience(resumeUuid, payload) {
    return http.post(`/api/v1/resumes/${resumeUuid}/experiences`, payload).then((r) => r.data);
  },

  deleteExperience(resumeUuid, experienceUuid) {
    return http.delete(`/api/v1/resumes/${resumeUuid}/experiences/${experienceUuid}`).then((r) => r.data);
  },
};
