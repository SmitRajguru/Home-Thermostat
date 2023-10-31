// #include <Arduino.h>
// #include <ESP8266HTTPClient.h>
// #include <ESP8266WiFi.h>
// #include <ArduinoJson.h>
// #include <DHT.h>

// #define POST_DATA false

// const char *ssid = "Attic";
// const char *password = "0147258369";

// int pollingRate = 10000;
// String Hostname = "DHT_Reporting_Node";
// String Hostname_local = "DHT_Display_Node";

// #define DHTPIN D7     // what pin we're connected to
// #define DHTTYPE DHT22 // DHT 22  (AM2302)

// DHT dht(DHTPIN, DHTTYPE); //// Initialize DHT sensor for normal 16mhz Arduino

// void oldsetup()
// {
//     Serial.begin(115200);
//     delay(10);

//     if (POST_DATA)
//     {
//         // Connect to WiFi network
//         Serial.println();
//         Serial.print("Connecting to ");
//         Serial.println(ssid);
//         WiFi.hostname(Hostname.c_str());
//         WiFi.begin(ssid, password);

//         while (WiFi.status() != WL_CONNECTED)
//         {
//             delay(500);
//             Serial.print(".");
//         }
//         Serial.println("");
//         Serial.println("WiFi connected");
//     }
//     else
//     {
//         WiFi.hostname(Hostname_local.c_str());
//     }
//     dht.begin();
// }

// String getJsonString(float humidity, float temprature, float tempFahrenheit)
// {
//     DynamicJsonDocument jsonData(1024);

//     jsonData["temprature"] = temprature;
//     jsonData["humidity"] = humidity;
//     jsonData["temprature_F"] = tempFahrenheit;

//     String jsonString;
//     serializeJson(jsonData, jsonString);
//     Serial.println(jsonString);
//     return jsonString;
// }

// void sendDHTData(String jsonString)
// {
//     WiFiClient client;
//     HTTPClient http; // Declare object of class HTTPClient

//     http.begin(client, "http://192.168.137.1:7000/DHTPost"); // Specify request destination
//     http.addHeader("Content-Type", "application/json");      // Specify content-type header

//     int httpCode = http.POST(jsonString); // Send the request
//     String payload = http.getString();    // Get the response payload

//     Serial.println(httpCode); // Print HTTP return code
//     Serial.println(payload);  // Print request response payload

//     http.end(); // Close connection
// }

// int timeSinceLastRead = 0;
// void oldloop()
// {
//     if (POST_DATA)
//     {
//         if (timeSinceLastRead > pollingRate)
//         {
//             if (WiFi.status() == WL_CONNECTED)
//             {
//                 // Check WiFi connection status
//                 String jsonString = getJsonString(dht.readHumidity(), dht.readTemperature(), dht.readTemperature(true));
//                 sendDHTData(jsonString);
//                 timeSinceLastRead = 0;
//             }
//             else
//             {
//                 Serial.println("Error in WiFi connection");
//             }
//         }
//         delay(100);
//         timeSinceLastRead += 100;
//     }
//     else
//     {

//         // Report every two seconds
//         if (timeSinceLastRead > 2000)
//         {
//             float h = dht.readHumidity();
//             float t = dht.readTemperature();
//             float f = dht.readTemperature(true);

//             // check if any failures and crash out to try again
//             if (isnan(h) || isnan(t) || isnan(f))
//             {
//                 Serial.println("Failed to read from DHT Sensor");
//                 timeSinceLastRead = 0;
//                 return;
//             }

//             // calculate heat index in Fahrenheit (default)
//             float hif = dht.computeHeatIndex(f, h);

//             // do same in Celsius
//             float hic = dht.computeHeatIndex(t, h, false);

//             Serial.print("Humidity: ");
//             Serial.print(h);
//             Serial.print(" %\t");
//             Serial.print("Temperature: ");
//             Serial.print(t);
//             Serial.print(" *C\t");
//             Serial.print(f);
//             Serial.print(" *F\t");
//             Serial.print("Heat index: ");
//             Serial.print(hic);
//             Serial.print(" *C\t");
//             Serial.print(hif);
//             Serial.println(" *F");

//             timeSinceLastRead = 0;
//         }
//         delay(100);
//         timeSinceLastRead += 100;
//     }
// }
