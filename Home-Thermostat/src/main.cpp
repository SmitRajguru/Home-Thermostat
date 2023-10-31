#include <Arduino.h>
#include <LEDIndicator.h>
#include <DHTSensor.h>
#include <AdafruitIOClient.h>

#define Loop_MS 100

bool isIOConnected = false;
unsigned long previousMillis = 0;
int ret;

void setup()
{
    // setup serial
    Serial.begin(115200);
    delay(10);

    // setup LED indicator
    LEDinit();

    // setup DHT sensor
    DHTinit();

    // setup Adafruit IO
    IOinit();

    previousMillis = millis();
}

void loop()
{
    if (millis() - previousMillis > Loop_MS)
    {
        // Check if we are connected to Adafruit IO
        if (!isIOConnected)
        {
            ret = IOCheckConnection();
            if (ret == -1)
            {
                LEDIONotConnected();
            }
            else
            {
                isIOConnected = true;
                LEDIOConnected();
                IOStatus();
                IOinitFeeds();
            }
        }
        else
        {
            // Update to the Adafruit IO server
            IOupdate();

            // Check if we are connected to Adafruit IO
            ret = IOCheckConnection();
            if (ret == -1)
            {
                isIOConnected = false;
                LEDIONotConnected();
                IOStatus();
                ESP.restart();
            }

            // Update the DHT sensor
            ret = DHTupdate();
            if (ret == -1)
                LEDDHTReadError();
            else if (ret == 1)
            {
                LEDDHTReadOK();
                ret = IOsendDHTData(DHTgetHumidity(), DHTgetTemprature(), DHTgetTempratureFahrenheit(), DHTgetHeatIndex(), DHTgetHeatIndexFahrenheit());
                if (ret == -1)
                {
                    LEDIOSendDataError();
                }
                else
                {
                    LEDIOSendDataOK();
                }
            }
        }
        previousMillis = millis();
    }

    // Update the LED indicator
    LEDupdate();
}
