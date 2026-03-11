import { ref } from "vue";
import { authApi } from "../api/auth";

export function useAuth() {
  const loading = ref(false);
  const error = ref("");

  async function register({ email, username, password, fio, role }) {
    loading.value = true;
    error.value = "";

    try {
      const data = await authApi.register({ email, username, password, fio, role });
      return data;
    } catch (e) {
      const status = e?.response?.status;

      if (status === 409) error.value = "Пользователь с таким email или username уже существует";
      else if (status === 422) error.value = "Неверное имя пользователя или пароль";
      else error.value = "Ошибка сервера или сети";

      throw e;
    } finally {
      loading.value = false;
    }
  }

  function setTokens({ access_token, refresh_token }) {
    localStorage.setItem("access_token", access_token);
    if (refresh_token) localStorage.setItem("refresh_token", refresh_token);
  }

  function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }

  async function login({ login, password }) {
    loading.value = true;
    error.value = "";

    try {
      const data = await authApi.login({ login, password });
      if (!data?.access_token) throw new Error("No access_token in response");
      setTokens(data);
      return data;
    } catch (e) {
      const status = e?.response?.status;

      if (status === 401) error.value = "Неверный логин или пароль";
      else if (status === 422) error.value = "Неверное имя пользователя или пароль";
      else if (status === 404) error.value = "Неверное имя пользователя или пароль";
      else error.value = "Ошибка сервера или сети";

      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      await authApi.logout();
    } finally {
      clearTokens();
    }
  }

  return { loading, error, login, register, logout, clearTokens };
}
