# syntax=docker/dockerfile:1
# Quick Dungeon: build the Hugo site, then serve it with Caddy.
ARG ALPINE_VERSION=3.22
ARG CADDY_VERSION=2.11

# --- Hugo toolchain (also used by `docker compose --profile dev up` for live preview)
FROM alpine:${ALPINE_VERSION} AS hugo
RUN apk add --no-cache hugo
ENV HUGO_CACHEDIR=/tmp/hugo_cache
WORKDIR /src

# --- Build the static site. Warnings (e.g. a missing image) fail the build.
FROM hugo AS build
COPY site/ ./
ARG BASE_URL=""
RUN hugo --gc --minify --panicOnWarning ${BASE_URL:+--baseURL "$BASE_URL"}

# --- Just the built files, for static hosts (Cloudflare):
#     docker build --target public --output type=local,dest=dist .
FROM scratch AS public
COPY --from=build /src/public /

# --- Serve it
FROM caddy:${CADDY_VERSION}-alpine
# The caddy binary carries cap_net_bind_service, so it can bind 80/443 without root.
RUN addgroup -S -g 10001 web \
 && adduser -S -D -H -u 10001 -G web web \
 && chown -R web:web /data /config
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /src/public /srv
ENV SITE_ADDRESS=:8080
USER web
EXPOSE 8080 80 443
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD wget -qO /dev/null http://127.0.0.1:8081/healthz || exit 1
