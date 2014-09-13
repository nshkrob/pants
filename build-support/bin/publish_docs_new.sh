#!/usr/bin/env bash
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

HERE=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

# We have special developer mode requirements - namely sphinx deps.
export PANTS_DEV=1

function usage() {
  echo "Publishes the http://pantsbuild.github.io/ docs locally or remotely."
  echo
  echo "Usage: $0 (-h|-opd)"
  echo " -h           print out this help message"
  echo " -o           open the doc site locally"
  echo " -p           publish the doc site remotely DISABLED FOR NOW"
  echo " -d           publish the site to a subdir at this path (useful for public previews)"

  if (( $# > 0 )); then
    die "$@"
  else
    exit 0
  fi
}

publish_path=""

while getopts "hopd:" opt; do
  case ${opt} in
    h) usage ;;
    o) preview="true" ;;
#   p) publish="true" ;;
    d) publish_path="${OPTARG}" ;;
    *) usage "Invalid option: -${OPTARG}" ;;
  esac
done

${HERE}/../../pants goal builddict --print-exception-stacktrace || \
  die "Failed to generate the 'BUILD Dictionary'."
cp dist/builddict/*.rst src/python/pants/docs/

function do_open() {
  if [[ "${preview}" = "true" ]]; then
    if which xdg-open &>/dev/null; then
      xdg-open $1
    elif which open &>/dev/null; then
      open $1
    else
      die "Failed to find an opener on your system for $1"
    fi
  fi
}

# generate some markdown as fodder for prototype doc site generator
${HERE}/../../pants goal markdown --markdown-fragment :: || \
  die "Failed to generate HTML from markdown'."

# invoke doc site generator
cp -f pants.ini pants.ini.sitegen
cat >> pants.ini.sitegen <<EOF
[backends]
packages: [
    'internal_backend.sitegen']
EOF
WRAPPER_REQUIREMENTS="src/python/internal_backend/sitegen/requirements.txt" PANTS_CONFIG_OVERRIDE=pants.ini.sitegen ${HERE}/../../pants goal sitegen --sitegen-config-path=src/python/pants/docs/docsite.yaml || \
  die "Failed to generate doc site'."

do_open "${HERE}/../../dist/docsite/index.html"

if [[ "${publish}" = "true" ]]; then
  url="http://pantsbuild.github.io/${publish_path}"
  read -ep "To abort publishing these docs to ${url} press CTRL-C, otherwise press enter to \
continue."
  (
    ${HERE}/../../src/python/pants/docs/publish_via_git.sh \
      git@github.com:pantsbuild/pantsbuild.github.io.git \
      ${publish_path} && \
    do_open ${url}/index.html
  ) || die "Publish to ${url} failed."
fi

