FROM nvidia/cuda:13.0.2-base-ubuntu24.04

# Установка средств сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

# Настройка non-root пользователя
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

USER nonroot

# Установка и настройка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Установка директории сборки
WORKDIR /src

# Установка зависимостей, генерация кеша
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,rw \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev

# Установка NLTK ресурсов
RUN uv run python -m nltk.downloader 'vader_lexicon'

# Перенос исходного кода
COPY . /src

# Установка проекта
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

ENV PATH="/src/.venv/bin:$PATH"
