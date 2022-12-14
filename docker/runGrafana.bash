#!/bin/bash
THEME="${GRAFANA_THEME:-light}"
/usr/bin/python3 /opt/patch.py -d /usr/share/grafana -c public/custom-css/custom.css -t "${THEME}"
cd /usr/share/grafana
/run.sh