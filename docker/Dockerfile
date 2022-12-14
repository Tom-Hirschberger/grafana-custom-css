FROM grafana/grafana:latest
USER root
COPY patch.py /opt/
COPY runGrafana.bash /opt/
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN mkdir -p /usr/share/grafana/custom-css && touch /usr/share/grafana/custom-css/custom.css && chmod 777 /opt/patch.py && chmod 777 /opt/runGrafana.bash
ENTRYPOINT ["/opt/runGrafana.bash"]