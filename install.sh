#!/usr/bin/sh

cd "$(dirname $0)"
mkdir -p build
meson setup build
ninja -C build/ install
killall liegensteuerung
liegensteuerung
