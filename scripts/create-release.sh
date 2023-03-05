#! /usr/bin/env sh

VERSION=$(grep -Po "version =\s\K.*" pyproject.toml)

cp -a calibre_libgen_store/. .cache/release
cp LICENSE .cache/release
echo "__version__ = $VERSION" > calibre_libgen_store/__version__.py
echo "from .store import LibGenStore" > .cache/release/__init__.py

mkdir -p dist
zip -j dist/calibre_libgen_store-$(echo $VERSION | tr -d '"').zip .cache/release/*