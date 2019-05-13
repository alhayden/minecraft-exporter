# minecraft-exporter
Prometheus exporter for minecraft statistics

## Use
Requires `prometheus_client` which can be installed via `pip` or from [the project's github page](https://github.com/prometheus/client_python)


To start exporting metrics, simply run `minecraft-exporter.py`, which will continually export metrics to the host's 8000 port until the program is stopped.
