

// Includes
#include <Arduino.h>
#include <AdafruitIO_WiFi.h>
#include <AdafruitIOClient.h>

// variables
AdafruitIO_WiFi io(IO_USERNAME, IO_KEY, WIFI_SSID, WIFI_PASS);
AdafruitIO_Feed *humidityFeed, *tempratureFeed, *tempFahrenheitFeed, *heatIndexFeed, *heatIndexFahrenheitFeed, *updateTriggerFeed;

/**
 * @brief Initializes the connection to Adafruit IO.
 *
 * This function initializes the connection to Adafruit IO using the credentials provided.
 * It prints a message to the Serial monitor indicating the connection process.
 */
void IOinit()
{
    // connect to io.adafruit.com
    Serial.print("Connecting to Adafruit IO");
    io.connect();
}

/**
 * @brief Checks the connection status to Adafruit IO.
 *
 * This function checks the connection status to Adafruit IO.
 * If the connection is not established, it prints a dot to the Serial monitor and returns -1.
 * If the connection is established, it prints the status text to the Serial monitor and returns 0.
 *
 * @return int Returns 0 if connected, -1 otherwise.
 */
int IOCheckConnection()
{
    // wait for a connection
    if (io.status() < AIO_CONNECTED)
    {
        Serial.print(".");
        return -1;
    }

    return 0;
}

/**
 * @brief Prints the connection status to Adafruit IO.
 *
 * This function prints the connection status to Adafruit IO to the Serial monitor.
 */
void IOStatus()
{
    // print the connection string to the serial monitor
    Serial.println();
    Serial.println(io.statusText());
}

/**
 * @brief Updates the Adafruit IO client.
 *
 * This function should always be present at the top of your loop function.
 * It keeps the client connected to io.adafruit.com, and processes any incoming data.
 */
void IOupdate()
{
    io.run();
}

void IOinitFeeds()
{
    // initialize feeds
    humidityFeed = io.feed(IO_HUMIDITY_FEED);
    tempratureFeed = io.feed(IO_TEMPRATURE_FEED);
    tempFahrenheitFeed = io.feed(IO_TEMPRATURE_FAHRENHEIT_FEED);
    heatIndexFeed = io.feed(IO_HEAT_INDEX_FEED);
    heatIndexFahrenheitFeed = io.feed(IO_HEAT_INDEX_FAHRENHEIT_FEED);
    updateTriggerFeed = io.feed(IO_UPDATE_TRIGGER_FEED);
}

/**
 * @brief Sends data to Adafruit IO.
 *
 * This function sends data to Adafruit IO.
 * It prints the data to the Serial monitor.
 *
 * @param feed The feed to send the data to.
 * @param data The data to send.
 */
void IOsendData(AdafruitIO_Feed *feed, float data)
{
    Serial.print("Sending data to Adafruit IO: ");
    Serial.print(feed->name);
    Serial.print(" -> ");
    Serial.println(data);
    feed->save(data);
}

/**
 * @brief Sends DHT data to Adafruit IO.
 *
 * This function sends DHT data to Adafruit IO.
 * It prints the data to the Serial monitor.
 *
 * @param humidity The humidity data to send.
 * @param temprature The temprature data to send.
 * @param tempFahrenheit The temprature in Fahrenheit data to send.
 * @param heatIndex The heat index data to send.
 * @param heatIndexFahrenheit The heat index in Fahrenheit data to send.
 */
int IOsendDHTData(float humidity, float temprature, float tempFahrenheit, float heatIndex, float heatIndexFahrenheit)
{
    // Send humidity data to Adafruit IO
    IOsendData(humidityFeed, humidity);

    // Send temprature data to Adafruit IO
    IOsendData(tempratureFeed, temprature);

    // Send temprature in Fahrenheit data to Adafruit IO
    IOsendData(tempFahrenheitFeed, tempFahrenheit);

    // Send heat index data to Adafruit IO
    IOsendData(heatIndexFeed, heatIndex);

    // Send heat index in Fahrenheit data to Adafruit IO
    IOsendData(heatIndexFahrenheitFeed, heatIndexFahrenheit);

    // Send update trigger data to Adafruit IO
    IOsendData(updateTriggerFeed, IO_UPDATE_TRIGGER);

    return 0;
}
