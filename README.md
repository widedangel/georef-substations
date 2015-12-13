

# Georeferencing of ENTSOE data


ENTSO-E has made available a [dataset](https://www.entsoe.eu/stum/) of
the European high voltage transmission network, for all countries
except Norway, Sweden, Cyprus and Iceland.

The dataset has abbreviated substation names and no location data for
the substations.

This project is an attempt to attach location data to the substations
based on the substations tagged in
[OpenStreetMap](http://www.openstreetmap.org/). The transmission
network can be see on [ITO World](http://product.itoworld.com/map/4).


The ENTSO-E STUM dataset is confidential and only downloadable upon
registration.

To use this code, copy the Excel files into a sub-directory called
"entsoe-data".

The goal is to fill the file
[matched-data/ucte-nodes.csv](matched-data/ucte-nodes.csv) with the
way ids which correspond to the substations.

The current best state can be seen at
[matched-data/europe.pdf](matched-data/europe.pdf).

There are snippets of code in [match_data.py](match_data.py) to help
do this matching, but much must be done by hand. The code snippets are
intended to be copied into the [iPython
notebook](http://ipython.org/).

The code is meant to help;
[matched-data/ucte-nodes.csv](matched-data/ucte-nodes.csv) must still
be filled out manually.
