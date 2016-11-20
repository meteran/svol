#!/usr/bin/env bash

DIR=/opt/svol

mkdir -p ${DIR}
cp svol.py ${DIR}/svol.py
chmod +x ${DIR}/svol.py
ln -s -f ${DIR}/svol.py /usr/local/bin/svol
echo "success"
