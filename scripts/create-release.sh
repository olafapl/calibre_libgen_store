#! /usr/bin/env sh

VERSION=$(grep -Po "version =\s\K.*" pyproject.toml | tr -d '"')
CACHE_DIR=.cache/release-$VERSION

echo "__version__ = \"$VERSION\"" > calibre_libgen_store/__version__.py

mkdir -p $CACHE_DIR
cp -a calibre_libgen_store/. $CACHE_DIR
cp LICENSE $CACHE_DIR
echo "from .store import LibGenStore" > $CACHE_DIR/__init__.py

mkdir -p dist
zip -j dist/calibre_libgen_store-$VERSION.zip $CACHE_DIR/*