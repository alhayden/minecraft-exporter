# minecraft-exporter
Prometheus exporter for minecraft statistics

## Use
Requires `prometheus_client` and `requests`.  Install them with `pip install -r requirements.txt`.


To start exporting metrics, simply run `minecraft-exporter.py`, which will continually export metrics to the host's 8000 port until the program is stopped.
