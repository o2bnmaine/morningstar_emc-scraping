# morningstar_emc-scraping
Python program that will poll for values from the Morningstar EMC-1 (specifically to get values for a TS-60)
This program will also poll for values from a Weatherflow weather station using REST api.

All results are inserted into a MariaDB table
Specific results are pushed to an ISY994 for immediate analysis -- this allows me to check if a DC circuit breaker on my solar array has flipped. This occurs when the boat hoist vibration causes an issue. :-/
