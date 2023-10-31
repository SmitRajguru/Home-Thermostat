#ifndef __LEDINDICATOR_H
#define __LEDINDICATOR_H

// Includes
#include <Arduino.h>
#include <FastLED.h>

// Defines
#define LED_Pin D5
#define LED_Count 1
#define LED_TYPE WS2812B
#define COLOR_ORDER GRB
#define BRIGHTNESS 20
#define FadeOutSpeed 5
#define LED_Blink_MS 100

const CRGB bootColor = CRGB::Blue;
const CRGB ioNotConnectedColor = CRGB::Red;
const CRGB ioConnectedColor = CRGB::Yellow;
const CRGB dhtReadErrorColor = CRGB::Orange;
const CRGB dhtReadOKColor = CRGB::Green;
const CRGB loopWaitingColor = CRGB::Violet;
const CRGB ioSendDataErrorColor = CRGB::Goldenrod;
const CRGB ioSendDataOKColor = CRGB::Blue;

// Function prototypes
void LEDinit();
void LEDupdate();
void LEDsetColor(int LED, CRGB color);
void LEDsetColors(CRGB color[]);
void LEDsetAll(CRGB color);

void LEDDHTReadError();
void LEDDHTReadOK();
void LEDIONotConnected();
void LEDIOConnected();
void LEDLoopWaiting();
void LEDIOSendDataError();
void LEDIOSendDataOK();

#endif
