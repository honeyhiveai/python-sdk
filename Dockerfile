FROM ghcr.io/astral-sh/uv:python3.11-alpine AS test-runner
RUN apk add --no-cache nodejs npm && \
    npm install -g @anthropic-ai/claude-code@2.1.190

WORKDIR /app

# Hatch resolves dynamic version/readme during uv sync, so copy metadata files
# before installing deps. Full source is copied in a later layer.
COPY pyproject.toml README.md ./
COPY src/honeyhive/__init__.py src/honeyhive/__init__.py

ENV UV_LINK_MODE=copy

RUN uv sync \
      --no-install-project \
      --all-packages \
      --extra dev \
      --extra openinference-openai \
      --extra openinference-anthropic \
      --extra openinference-claude-agent-sdk

COPY . .

ENTRYPOINT [ "uv", "run", "--extra", "dev" ]

# Extra instrumentors enable paid provider tests. Keep them opt-in for image consumers.
FROM test-runner AS live-provider-tests
RUN uv sync --inexact \
      --extra dev \
      --extra openinference-openai-agents \
      --extra openinference-langchain \
      --extra traceloop-openai \
      --extra traceloop-anthropic \
      --extra traceloop-langchain

# Builds without an explicit target retain the standard integration dependencies.
FROM test-runner AS default
