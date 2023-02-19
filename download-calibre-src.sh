#! /usr/bin/env/sh

mkdir -p .cache
git clone https://github.com/kovidgoyal/calibre.git .cache/calibre
cp -r .cache/calibre/src/calibre calibre
rm -rf .cache/calibre