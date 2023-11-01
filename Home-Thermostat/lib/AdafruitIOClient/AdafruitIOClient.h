#ifndef __ADAFRUITIOCLIENT_H
#define __ADAFRUITIOCLIENT_H

// Includes
#include <Arduino.h>
#include <AdafruitIO_WiFi.h>
#include <SECRETS.h>

#define IO_HUMIDITY_FEED "thermostat.humidity"
#define IO_TEMPRATURE_FEED "thermostat.temprature-c"
#define IO_TEMPRATURE_FAHRENHEIT_FEED "thermostat.temprature-f"
#define IO_HEAT_INDEX_FEED "thermostat.heatindex-c"
#define IO_HEAT_INDEX_FAHRENHEIT_FEED "thermostat.heatindex-f"
#define IO_UPDATE_TRIGGER_FEED "thermostat.update-trigger"

#define IO_UPDATE_TRIGGER 1

#define IO_UPDATE_MS 10000

// Function prototypes
void IOinit();
int IOCheckConnection();
void IOStatus();
void IOupdate();
void IOinitFeeds();
int IOsendDHTData(float humidity, float temprature, float tempFahrenheit, float heatIndex, float heatIndexFahrenheit);

#endif