#!/usr/bin/sh

cd "$(dirname $0)"
ninja -C build/ install
killall liegensteuerung
liegensteuerung
