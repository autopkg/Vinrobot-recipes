FROM mcr.microsoft.com/devcontainers/base:trixie

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

RUN set -ex \
	&& apt update \
	&& apt install -y \
		build-essential \
		libffi-dev \
		libxml2-dev \
		libxslt1-dev

RUN set -ex \
	&& cd /opt \
	&& git clone --depth=1 --branch=v2.9.0 https://github.com/autopkg/autopkg.git

RUN set -ex \
	&& cd /opt/autopkg \
	&& export UV_PYTHON_INSTALL_DIR=/opt/autopkg/Python \
	&& uv python pin 3.11 \
	&& uv venv \
	&& uv pip install -r requirements.txt

COPY autopkg /usr/local/bin/
