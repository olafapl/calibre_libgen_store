#! /usr/bin/env sh

VERSION=$(grep -Po "version =\s\K.*" pyproject.toml)
echo "__version__ = $VERSION" > calibre_libgen_store/__version__.py

cp -a calibre_libgen_store/. .cache/release
cp LICENSE .cache/release
echo "from .store import LibGenStore" > .cache/release/__init__.py

mkdir -p dist
zip -rj dist/calibre_libgen_store-$(echo $VERSION | tr -d '"').zip .cache/release -i /*.py