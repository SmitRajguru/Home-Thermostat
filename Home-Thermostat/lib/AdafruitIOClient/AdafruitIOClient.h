#ifndef __ADAFRUITIOCLIENT_H
#define __ADAFRUITIOCLIENT_H

// Includes
#include <Arduino.h>
#include <AdafruitIO_WiFi.h>
#include <SECRETS.h>

#define IO_UPDATE_MS 10000

// Function prototypes
void IOinit();
int IOCheckConnection();
void IOStatus();
void IOupdate();
void IOinitFeeds();
int IOsendDHTData(float humidity, float temprature, float tempFahrenheit, float heatIndex, float heatIndexFahrenheit);

#endif