#include <Arduino.h>
#include <LEDIndicator.h>
#include <FastLED.h>

// variables
CRGB LED_Values[LED_Count];

bool isBlinking = false;
CRGB blinkColor = CRGB::Red;
unsigned long previousLedMillis = 0;

/**
 * @brief Initializes the LED indicator.
 *
 * This function initializes the LED indicator.
 * It should be called in the setup() function of your Arduino sketch.
 *
 * @param none
 */
void LEDinit()
{
    // Uncomment/edit one of the following lines for your leds arrangement.
    // ## Clockless types ##
    FastLED.addLeds<NEOPIXEL, LED_Pin>(LED_Values, LED_Count); // GRB ordering is assumed
    // FastLED.addLeds<SM16703, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<TM1829, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<TM1812, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<TM1809, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<TM1804, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<TM1803, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<UCS1903, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<UCS1903B, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<UCS1904, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<UCS2903, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<WS2812, LED_Pin, RGB>(LED_Values,LED_Count);  // GRB ordering is typical
    // FastLED.addLeds<WS2852, LED_Pin, RGB>(LED_Values,LED_Count);  // GRB ordering is typical
    // FastLED.addLeds<WS2812B, LED_Pin, RGB>(LED_Values,LED_Count);  // GRB ordering is typical
    // FastLED.addLeds<GS1903, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<SK6812, LED_Pin, RGB>(LED_Values,LED_Count);  // GRB ordering is typical
    // FastLED.addLeds<SK6822, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<APA106, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<PL9823, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<SK6822, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<WS2811, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<WS2813, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<APA104, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<WS2811_400, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<GE8822, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<GW6205, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<GW6205_400, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<LPD1886, LED_Pin, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<LPD1886_8BIT, LED_Pin, RGB>(LED_Values,LED_Count);
    // ## Clocked (SPI) types ##
    // FastLED.addLeds<LPD6803, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);  // GRB ordering is typical
    // FastLED.addLeds<LPD8806, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);  // GRB ordering is typical
    // FastLED.addLeds<WS2801, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<WS2803, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<SM16716, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);
    // FastLED.addLeds<P9813, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);  // BGR ordering is typical
    // FastLED.addLeds<DOTSTAR, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);  // BGR ordering is typical
    // FastLED.addLeds<APA102, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);  // BGR ordering is typical
    // FastLED.addLeds<SK9822, LED_Pin, CLOCK_PIN, RGB>(LED_Values,LED_Count);  // BGR ordering is typical

    // Default the LED indicator to RED
    LEDsetAll(bootColor);

    // Set the brightness
    FastLED.setBrightness(BRIGHTNESS);

    // show the LED indicator
    FastLED.show();
}

/**
 * @brief Update the LED indicator
 *
 * This function updates the LED indicator.
 *
 * @param none
 */
void LEDupdate()
{
    if (isBlinking)
    {
        unsigned long currentMillis = millis();
        if (currentMillis - previousLedMillis >= LED_Blink_MS)
        {
            if (LED_Values[0] == CRGB::Black)
                LEDsetAll(blinkColor);
            else
                LEDsetAll(CRGB::Black);
        }
        // Serial.println("Blink the LED indicator");
    }
    else
    {
        // Fade out the LED indicator
        for (int i = 0; i < LED_Count; i++)
        {
            LED_Values[i].fadeToBlackBy(FadeOutSpeed);
        }
        // Serial.println("Fade out the LED indicator");
    }

    FastLED.show();
}

/**
 * @brief Set the LED to a color
 *
 * This function sets the LED to a color.
 *
 * @param LED The LED to set.
 * @param color The color to set the LED to.
 */
void LEDsetColor(int LED, CRGB color)
{
    LED_Values[LED] = color;
}

/**
 * @brief Set the LEDs to an array of colors
 *
 * This function sets the LEDs to an array of colors.
 *
 * @param color The array of colors to set the LEDs to.
 */
void LEDsetColors(CRGB color[])
{
    for (int i = 0; i < LED_Count; i++)
    {
        LEDsetColor(i, color[i]);
    }
}

/**
 * @brief Set the LEDs to a single color
 *
 * This function sets the LEDs to a single color.
 *
 * @param color The color to set the LEDs to.
 */
void LEDsetAll(CRGB color)
{
    for (int i = 0; i < LED_Count; i++)
    {
        LEDsetColor(i, color);
    }
}

/**
 * @brief Set the LED indicator to DHT Read Error
 *
 * This function sets the LED indicator to dhtReadErrorColor.
 *
 * @param none
 */
void LEDDHTReadError()
{
    isBlinking = true;
    blinkColor = dhtReadErrorColor;
    previousLedMillis = 0;
}

/**
 * @brief Set the LED indicator to DHT Read OK
 *
 * This function sets the LED indicator to dhtReadOKColor.
 *
 * @param none
 */
void LEDDHTReadOK()
{
    LEDsetAll(dhtReadOKColor);
    isBlinking = false;
}

/**
 * @brief Set the LED indicator to Adafruit IO Connected
 *
 * This function sets the LED indicator to ioConnectedColor.
 *
 * @param none
 */
void LEDIOConnected()
{
    LEDsetAll(ioConnectedColor);
    isBlinking = false;
}

/**
 * @brief Set the LED indicator to Adafruit IO Not Connected
 *
 * This function sets the LED indicator to ioNotConnectedColor.
 *
 * @param none
 */
void LEDIONotConnected()
{
    isBlinking = true;
    blinkColor = ioNotConnectedColor;
    previousLedMillis = 0;
}

/**
 * @brief Set the LED indicator to Loop Waiting
 *
 * This function sets the LED indicator to loopWaitingColor.
 *
 * @param none
 */
void LEDLoopWaiting()
{
    LEDsetAll(loopWaitingColor);
    isBlinking = false;
}

/**
 * @brief Set the LED indicator to Adafruit IO Send Data Error
 *
 * This function sets the LED indicator to dhtReadErrorColor.
 *
 * @param none
 */
void LEDIOSendDataError()
{
    isBlinking = true;
    blinkColor = ioSendDataErrorColor;
    previousLedMillis = 0;
}

/**
 * @brief Set the LED indicator to Adafruit IO Send Data OK
 *
 * This function sets the LED indicator to dhtReadOKColor.
 *
 * @param none
 */
void LEDIOSendDataOK()
{
    LEDsetAll(ioSendDataOKColor);
    isBlinking = false;
}
