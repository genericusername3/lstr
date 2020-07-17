#!/usr/bin/sh

cd "$(dirname $0)"
mkdir -p build
ninja -C build/ install
killall liegensteuerung
liegensteuerung
