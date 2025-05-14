# RMK_internship_2025

## Approach

* Static walking times:
  * 300 seconds: Home → Departure bus stop
  * 240 seconds: Destination bus stop → Meeting
* Variable bus commute times:
  * Will be calculated based on collected data
  * Primary method: Calculate mean trip duration for each route

## Data Sources

* GTFS data: [Peatus.ee GTFS feed](https://peatus.ee/gtfs/)
* Documentation about the GTFS data: [Public transport register specification](https://www.agri.ee/sites/default/files/documents/2023-07/%C3%BChistranspordiregister-avaandmed-spetsifikatsioon-v1_4.pdf) (v1.4)

## Next Steps

* Implement data collection pipeline
* Develop calculation methodology for mean trip durations
* Create trip time estimation algorithm
* Probabilities and plotting