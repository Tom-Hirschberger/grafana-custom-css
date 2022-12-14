# Grafana custom css Docker integration

If you want to run Grafana with the original Grafana docker image but you want to patch it anyway you can use the files within this directory to create a custom docker image with the patch included.

## Create Image

You need to change to this directory and build the custom image with the included `Dockerfile`. Choose the tag you like by replacing `<TAG>` with your custom tag (i.e "grafana/mygrafana:latest"):

```
docker build -t <TAG> .
```

## RUN a container with the new image

You need to map the file containing your custom.css definitions to the location `/usr/share/grafana/custom-css/custom.css` within the container:

```
docker run -v /path/on/the/host.css:/usr/share/grafana/custom-css/custom.css <TAG>
```
