// Includes
#include <Arduino.h>
#include <DHTSensor.h>
#include <DHT.h>

// variables
DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino

float humidity = 0;
float temprature = 0;
float tempFahrenheit = 0;

float heatIndex = 0;
float heatIndexFahrenheit = 0;

unsigned long previousREADMillis = 0;

/**
 * @brief Initializes the DHT sensor.
 *
 * This function initializes the DHT sensor and sets up the data pin and sensor type.
 * It should be called in the setup() function of your Arduino sketch.
 */
void DHTinit()
{
    dht.begin();
}

/**
 * @brief Reads data from the DHT sensor.
 *
 * This function reads the humidity, temperature, and heat index from the DHT sensor.
 * It prints the sensor data to the Serial monitor.
 *
 * @return int Returns 1 if the read operation was successful, -1 if it failed, and 0 otherwise.
 */
int DHTupdate()
{
    // check if we need to update the DHT sensor
    if (millis() - previousREADMillis > DHT_UPDATE_MS || previousREADMillis == 0)
    {
        float h = dht.readHumidity();
        float t = dht.readTemperature();
        float f = dht.readTemperature(true);

        // check if any failures and crash out to try again
        if (isnan(h) || isnan(t) || isnan(f))
        {
            Serial.println("Failed to read from DHT Sensor");
            previousREADMillis = 0;
            return -1;
        }

        humidity = h;
        temprature = t;
        tempFahrenheit = f;

        // calculate heat index in Fahrenheit (default)
        heatIndexFahrenheit = dht.computeHeatIndex(f, h);

        // do same in Celsius
        heatIndex = dht.computeHeatIndex(t, h, false);

        Serial.print("DHT Sensor Data: \t");
        Serial.print("Humidity: ");
        Serial.print(h);
        Serial.print(" %\t");
        Serial.print("Temperature: ");
        Serial.print(t);
        Serial.print(" *C\t");
        Serial.print(f);
        Serial.print(" *F\t");
        Serial.print("Heat index: ");
        Serial.print(heatIndex);
        Serial.print(" *C\t");
        Serial.print(heatIndexFahrenheit);
        Serial.println(" *F");

        previousREADMillis = millis();
        return 1;
    }
    return 0;
}

/**
 * @brief Gets the humidity value.
 *
 * This function returns the last read humidity value from the DHT sensor.
 *
 * @return float Returns the humidity value.
 */
float DHTgetHumidity()
{
    return humidity;
}

/**
 * @brief Gets the temperature value.
 *
 * This function returns the last read temperature value from the DHT sensor.
 *
 * @return float Returns the temperature value.
 */
float DHTgetTemprature()
{
    return temprature;
}

/**
 * @brief Gets the temperature value in Fahrenheit.
 *
 * This function returns the last read temperature value from the DHT sensor in Fahrenheit.
 *
 * @return float Returns the temperature value in Fahrenheit.
 */
float DHTgetTempratureFahrenheit()
{
    return tempFahrenheit;
}

/**
 * @brief Gets the heat index value.
 *
 * This function returns the last read heat index value from the DHT sensor.
 *
 * @return float Returns the heat index value.
 */
float DHTgetHeatIndex()
{
    return heatIndex;
}

/**
 * @brief Gets the heat index value in Fahrenheit.
 *
 * This function returns the last read heat index value from the DHT sensor in Fahrenheit.
 *
 * @return float Returns the heat index value in Fahrenheit.
 */
float DHTgetHeatIndexFahrenheit()
{
    return heatIndexFahrenheit;
}

/**
 * @brief Gets the sensor data in JSON format.
 *
 * This function returns the last read sensor data from the DHT sensor in JSON format.
 *
 * @return String Returns the sensor data in JSON format.
 */
String DHTgetJsonStringData()
{
    String jsonString = "{\"humidity\":";
    jsonString += humidity;
    jsonString += ",\"temprature\":";
    jsonString += temprature;
    jsonString += ",\"tempFahrenheit\":";
    jsonString += tempFahrenheit;
    jsonString += ",\"heatIndex\":";
    jsonString += heatIndex;
    jsonString += ",\"heatIndexFahrenheit\":";
    jsonString += heatIndexFahrenheit;
    jsonString += "}";

    return jsonString;
}