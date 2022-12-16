# Grafana custom css Docker integration

If you want to run Grafana with the original Grafana docker image but you want to patch it anyway you can use the files within this directory to create a custom docker image with the patch included.

## Create Image

You need to change to this directory and build the custom image with the included `Dockerfile`. Choose the tag you like by replacing `<TAG>` with your custom tag (i.e "grafana/mygrafana:latest"):

```bash
docker build -t <TAG> .
```

## RUN a container with the new image

You need to map the file containing your custom.css definitions to the location `/usr/share/grafana/custom-css/custom.css` within the container:

```bash
docker run -v /path/on/the/host.css:/usr/share/grafana/custom-css/custom.css <TAG>
```


## Synology Docker integration

Login to your NAS with SSH...

### Transfer the code to your nas

Download the current main branch:

```bash
wget https://github.com/Tom-Hirschberger/grafana-custom-css/archive/refs/heads/main.zip
```

Extract it:

```bash
7z x main.zip
```

### Change to the code repostory

```bash
cd grafana-custom-css-main/docker/
```

### Create the image

```bash
sudo docker build -t grafana:mygrafana .
```

### Use it

Change the image of your Grafana container to the new `grafana:mygrafana` image.