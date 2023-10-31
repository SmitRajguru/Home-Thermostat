#ifndef __DHTSENSOR_H
#define __DHTSENSOR_H

// Includes
#include <Arduino.h>
#include <DHT.h>

#define DHTPIN D7     // what pin we're connected to
#define DHTTYPE DHT22 // DHT 22  (AM2302)s

#define DHT_UPDATE_MS 30000

// Function prototypes
void DHTinit();
int DHTupdate();
float DHTgetHumidity();
float DHTgetTemprature();
float DHTgetTempratureFahrenheit();
float DHTgetHeatIndex();
float DHTgetHeatIndexFahrenheit();
String DHTgetJsonStringData();

#endif