# Architecture

The digital twin architecture will use a conectivity layer, data layer and a domain layer.

In the domain layer, we have 

In the conectivity layer:
- Data Acquisition layer
- Data Preprocessing Layer
- Data Integration layer


The ideia is that the DT will receive information from an huge number of conected devices, process this data, unify it, eavaluate the scenario and control all this devices. For this reason, the data gathering should be modular, enabling new devices to plugin. For this reason, the conectivity layer should have specific adapters for a specific device, for example, a new PSU will send data for a PSU module that knows how to speak with this PSU and translates DT commands to the PSU. This will make necessary 