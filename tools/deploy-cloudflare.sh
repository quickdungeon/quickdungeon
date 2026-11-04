#!/bin/sh
# Build the site with the Docker Hugo toolchain and deploy it to Cloudflare (Workers static
# assets, free plan). Needs Docker and Node. .github/workflows/deploy.yml runs this on every
# push; to run it yourself, sign in once first with: npx wrangler@4 login
#
# Usage: tools/deploy-cloudflare.sh             build, then deploy
#        tools/deploy-cloudflare.sh --dry-run   build and check, upload nothing
#        tools/deploy-cloudflare.sh --preview   build, then serve it at http://localhost:8787
#                                               the way Cloudflare would (headers, 404 page)
set -eu
cd "$(dirname "$0")/.."

# Start from an empty dist/ so files from earlier builds don't get uploaded.
rm -rf dist
log=$(mktemp)
if ! docker build --progress=plain --target public --output type=local,dest=dist . >"$log" 2>&1; then
  cat "$log" >&2  # the full log, so Hugo's warning (which fails the build) is visible
  rm -f "$log"
  echo "build failed" >&2
  exit 1
fi
rm -f "$log"
echo "built $(find dist -type f | wc -l) files into dist/"

if [ "${1:-}" = "--preview" ]; then
  exec npx --yes wrangler@4 dev --port 8787
fi
exec npx --yes wrangler@4 deploy "$@"
