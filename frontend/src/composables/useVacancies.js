import { computed, reactive, ref } from "vue";
import { vacanciesApi } from "../api/vacancies";

function buildParams({ query, filters, cursor, cursorUuid, limit }) {
  const params = {
    remote: filters.remote,
    city: filters.city || undefined,
    salary_from: filters.salary_from || undefined,
    salary_to: filters.salary_to || undefined,
    include_archived: false,
    company_id: filters.company_id || undefined,
    cursor: cursor || undefined,
    cursor_uuid: cursorUuid || undefined,
    limit: limit || 10,
  };

  if (query && query.trim()) params.vacancy_title = query.trim();
  return params;
}

function hasActiveFilters(filters) {
  return Boolean(
    filters.remote !== null
      || String(filters.city || "").trim()
      || String(filters.salary_from || "").trim()
      || String(filters.salary_to || "").trim()
      || String(filters.company_id || "").trim()
  );
}

export function useVacancies() {
  const items = ref([]);
  const loading = ref(false);
  const loadingMore = ref(false);
  const error = ref("");

  const query = ref("");

  const filters = reactive({
    remote: null,
    city: "",
    salary_from: "",
    salary_to: "",
    company_id: "",
  });

  const mode = ref("recommendations");

  const limit = 10;
  const cursor = ref(null);
  const cursorUuid = ref(null);
  const hasMore = ref(true);

  function computeNextCursor(list) {
    if (!list || list.length === 0) return null;
    const last = list[list.length - 1];
    return { createdAt: last.created_at, uuid: last.uuid };
  }

  function reset() {
    items.value = [];
    cursor.value = null;
    cursorUuid.value = null;
    hasMore.value = true;
    error.value = "";
  }

  async function loadFirst() {
    loading.value = true;
    loadingMore.value = false;
    error.value = "";
    reset();

    try {
      const q = query.value.trim();
      const filtersApplied = hasActiveFilters(filters);

      if (!q && !filtersApplied) {
        mode.value = "recommendations";

        const params = buildParams({
          query: "",
          filters,
          cursor: null,
          cursorUuid: null,
          limit,
        });

        try {
          const data = await vacanciesApi.getRecommendations(params);
          items.value = data || [];
        } catch (e) {
          if (e?.response?.status !== 404) throw e;

          mode.value = "all";
          const data = await vacanciesApi.getAll(params);
          items.value = data || [];
        }
      } else if (q) {
        mode.value = "search";

        const params = buildParams({
          query: q,
          filters,
          cursor: null,
          cursorUuid: null,
          limit,
        });

        const data = await vacanciesApi.search(params);
        items.value = data || [];
      } else {
        mode.value = "all";

        const params = buildParams({
          query: "",
          filters,
          cursor: null,
          cursorUuid: null,
          limit,
        });

        const data = await vacanciesApi.getAll(params);
        items.value = data || [];
      }

      const next = computeNextCursor(items.value);
      cursor.value = next?.createdAt || null;
      cursorUuid.value = next?.uuid || null;
      hasMore.value = Boolean(cursor.value && cursorUuid.value && items.value.length >= limit);
    } catch (e) {
      const status = e?.response?.status;

      if (status === 401) error.value = "Вы не авторизованы";
      else if (status === 404) error.value = "Вакансии не найдены";
      else error.value = "Ошибка сервера или сети";

      hasMore.value = false;
    } finally {
      loading.value = false;
    }
  }

  async function loadMore() {
    if (loading.value || loadingMore.value) return;
    if (!hasMore.value) return;

    loadingMore.value = true;
    error.value = "";

    try {
      const q = query.value.trim();

      const params = buildParams({
        query: q,
        filters,
        cursor: cursor.value,
        cursorUuid: cursorUuid.value,
        limit,
      });

      let data;

      if (mode.value === "search") data = await vacanciesApi.search(params);
      else if (mode.value === "recommendations") data = await vacanciesApi.getRecommendations(params);
      else data = await vacanciesApi.getAll(params);

      const batch = data || [];

      if (batch.length === 0) {
        hasMore.value = false;
        return;
      }

      items.value = items.value.concat(batch);

      const next = computeNextCursor(batch);
      cursor.value = next?.createdAt || null;
      cursorUuid.value = next?.uuid || null;
      hasMore.value = Boolean(cursor.value && cursorUuid.value && batch.length >= limit);
    } catch (e) {
      const status = e?.response?.status;

      if (status === 401) error.value = "Вы не авторизованы";
      else error.value = "Ошибка сервера или сети";

      hasMore.value = false;
    } finally {
      loadingMore.value = false;
    }
  }

  const isEmpty = computed(() => !loading.value && items.value.length === 0);

  return {
    items,
    loading,
    loadingMore,
    error,
    query,
    filters,
    mode,
    hasMore,
    isEmpty,
    loadFirst,
    loadMore,
    reset,
  };
}
