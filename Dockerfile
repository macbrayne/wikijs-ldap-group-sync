FROM python:3.10-slim-buster as base

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libsasl2-dev libldap2-dev
WORKDIR /wikijs_ldap_group_sync


FROM base as builder
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.0.5 \
    DEBIAN_FRONTEND=noninteractive

RUN pip install "poetry"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && poetry install --no-dev --no-root

COPY . .
RUN . /venv/bin/activate && poetry build

FROM base as final

COPY --from=builder /venv /venv
COPY --from=builder /wikijs_ldap_group_sync/dist .
COPY docker-entrypoint.sh ./


RUN . /venv/bin/activate
RUN pip install *.whl

CMD ["./docker-entrypoint.sh"]