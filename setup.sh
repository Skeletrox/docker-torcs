#!/bin/sh

export CFLAGS="-fPIC"
export CPPFLAGS=$CFLAGS
export CXXFLAGS=$CFLAGS
git clone https://github.com/fmirus/torcs-1.3.7.git
cd torcs-1.3.7
./configure --prefix=$(pwd)/BUILD
make && make install && make datainstall

echo "setup complete"