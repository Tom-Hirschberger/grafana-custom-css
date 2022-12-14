# Grafana custom css

As Grafana does not provide any way to make the background of embedded panels transparent or change any style i wrote a small script that patches the "index.html" of Grafana to include a custom css file if a specific theme is active.
The script registers as a system service and checks the file at each reboot. This way even if the Grafana file is overriden during a update the patch will be activated after the next reboot.

:warning: **Even it the patch process is automated it is a ugly hack. It might work with future versions but it might not!**  

The script is tested with the following scenario:

* Grafana 9.2.5 on Ubuntu 22.04 and Raspberry OS (Bullseye 32Bit)
* Grafana directory is `/usr/share/grafana` (can be changed with command line option)

## Installation

Clone the repository to the home directory of your user:

```bash
cd $HOME
git clone https://github.com/Tom-Hirschberger/grafana-custom-css.git
cd grafana-custom-css
```

Register the service and do the inital patch:

```bash
sudo ./patch.py -r
```

Restart the Grafana service:

```bash
sudo systemctl restart grafana-server.service
```

## Debugging

If want to make sure that the patch worked you can take a look to the output of the service script (exit with `q`):

```bash
sudo systemctl status grafana-custom-css.service
```

or into its journal (exit with `:q`):

```bash
sudo journalctl -u grafana-custom-css.service
```

## Grafana panel embedding

The default setting of the script is to patch the `light` theme. So if this theme is active the background of the panels will be transparent!

Make sure that the embedding url looks something like:

```text
https://mygrafana:3000/d-solo/ABCDEFGHI/temperaturen?orgId=1&from=1670417464199&to=1670439064199&theme=light&panelId=6
```

and contains the part:

```text
&theme=light
```

## Uninstalling the patch

If you are unhappy with the patch and want it to be removed run the following commands:

```bash
cd $HOME/grafana-custom-css
sudo ./patch.py -u
```
