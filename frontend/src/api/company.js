import { http } from "./http";

export const companyApi = {
  getById(uuid) {
    return http.get(`/api/v1/companies/${uuid}`).then((r) => r.data);
  },
};