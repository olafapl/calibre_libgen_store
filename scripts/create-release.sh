#! /usr/bin/env sh

VERSION=$(grep -Po "version =\s\K.*" pyproject.toml)
echo "__version__ = $VERSION" > calibre_libgen_store/__version__.py
mkdir -p dist
cp -a calibre_libgen_store/. .cache/build
echo "from .store import LibGenStore" > .cache/build/__init__.py
zip -rj dist/calibre_libgen_store$(echo $VERSION | tr -d '"').zip .cache/build -i /*.py