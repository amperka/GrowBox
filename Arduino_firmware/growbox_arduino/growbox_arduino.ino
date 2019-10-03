/* GrowBoard receives data from several sensors: temperature, CO2, pH, Water level sensor
and TDS and sends them via the serial port to Raspberry Pi every 2 seconds. It accepts commands from
Rasberry through the serial port and controls the ON/OFF of the LED lamp, fan and compressor.
Real Time is tracked by Troyka RTC module.
Sensors:
1) Temperature - DS18B20 (DallasTemperature lib), One Wire interface
2) CO2 - CCS811 (Adafruit_CCS811 lib), I2C interface
3) pH - analog sensor, connect to A3 pin,
   example from https://wiki.dfrobot.com/PH_meter_SKU__SEN0161_
4) TDS - analog sensor, connect to A2 pin,
   example from https://wiki.dfrobot.com/Gravity__Analog_TDS_Sensor___Meter_For_Arduino_SKU__SEN0244
5) Water level sensor - digital sensor, connect to 7 pin.
6) Real time - Troyka RTC module (TroykaRTC lib), I2C interface.
Activities:
1) LED Lamp connect to 8 pin through Troyka Mini Relay module
2) Fan connect to 10 pin through Troyka Power Key module
3) Compressor connect to 9 pin through Troyka Power Key module
*/
#include <Adafruit_CCS811.h>
#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <OneWire.h>
#include <TroykaRTC.h>
#include <Wire.h>

#define EEPROM_ADDR 0
// Pins
#define LAMP_PIN 8 // Lamp
#define COMP_PIN 9 // Compressor
#define FAN_PIN 10 // Fan
#define LVL_PIN 7 // Water Level
#define PH_PIN A3 // pH sensor
#define TDS_PIN A2 // TDS sensor
#define ONE_WIRE_BUS 6 // Temperature (ds18b20)
// Settings for measurments
#define PH_ARR_LEN 40 // Number of samples of pH sensor
#define VREF 5.0 // Analog reference voltage(Volt) of the ADC
#define TDS_ARR_LEN 30 // Number of samples of TDS sensor
// Time intervals
#define PRINT_TIME 2000 // Data printing interval
#define SAMPLE_TIME 20 // Measurment interval for pH and TDS
#define ONE_MINUTE 60000 // One minute interval for fan
#define LAMP_ON_TIME 5 // Lamp On time
// Date and time arrays size
#define LEN_TIME 12 // Size of time array
#define LEN_DATE 12 // Size of date array
#define LEN_DOW 12 // Size of day array

// pH
int pHArray[PH_ARR_LEN]; // Store the average value of the sensor feedback
int pHArrayIndex = 0;
float aCoeff = 0; // pH calibration coefficient "a"
float bCoeff = 0; // pH calibration coefficient "b"
float accFour = 0; // Additional variable to calculate pH coefficient (4.0 point)
float accSeven = 0; // Additional variable to calculate pH coefficient (7.0 point)

// Water Level
int lvlState = 0;

// TDS
int tdsBuffer[TDS_ARR_LEN]; // Store the analog value from TDS sensor in the array, read from ADC
int tdsBufferTemp[TDS_ARR_LEN]; // Temporary TDS array
int tdsBufferIndex = 0;
float averageVoltage = 0;
float tdsValue = 0;
float temperature = 25.0; //temperature compensation (25 *C by default)

// Temperature(ds18b20)
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

// CO2 sensor
Adafruit_CCS811 ccs;
RTC clock;

char time[LEN_TIME]; // Time array
char date[LEN_DATE]; // Date array
char weekDay[LEN_DOW]; // Current day of week array
int lampState = 0; // Current lamp state
int lampOn = 0; // Command from RPi to switch lamp
int compressorOn = 0; // Command from RPi to switch compressor
int fanOn = 0; // Command from RPi to switch fan
float fanTime = 0; // Working time from fan from RPi
boolean fanState = true; // Current fan state
unsigned long lastFanTime = 0;
String commandStr = ""; // Raw command string from RPi

void setup(void) {
    long res1 = 0, res2 = 0;
    // Read current pH sensor's "a" and "b" coefficients in temporary variables
    EEPROM.get(EEPROM_ADDR, res1);
    EEPROM.get(EEPROM_ADDR + 50, res2);
    // If res1 and res2 are equal to 0xFFFFFFFF
    if (res1 == -1 || res2 == -1) {
        aCoeff = 0;
        bCoeff = 0;
    } else {
        EEPROM.get(EEPROM_ADDR, aCoeff); // Read current pH sensor's "a" coefficient
        EEPROM.get(EEPROM_ADDR + 50, bCoeff); // Read current pH sensor's "b" coefficient
    }
    Serial.begin(9600);
    pinMode(TDS_PIN, INPUT);
    tempSensor.begin();
    ccs.begin();
    while (!ccs.available())
        ;
    float temp = ccs.calculateTemperature();
    ccs.setTempOffset(temp - 25.0);
    pinMode(LAMP_PIN, OUTPUT);
    pinMode(FAN_PIN, OUTPUT);
    pinMode(COMP_PIN, OUTPUT);
    clock.begin();
}

void loop(void) {
    // Compressor ON/OFF
    if (compressorOn) {
        digitalWrite(COMP_PIN, HIGH);
    } else {
        digitalWrite(COMP_PIN, LOW);
    }

    // Fan ON/OFF
    if (fanOn) {
        if (fanState) {
            digitalWrite(FAN_PIN, HIGH);
            if (millis() - lastFanTime > fanTime * ONE_MINUTE) {
                lastFanTime = millis();
                fanState = false;
            }
        } else {
            digitalWrite(FAN_PIN, LOW);
            if (millis() - lastFanTime > 2 * ONE_MINUTE) {
                lastFanTime = millis();
                fanState = true;
            }
        }
    } else {
        digitalWrite(FAN_PIN, LOW);
    }

    static unsigned long samplingTime = millis();
    static unsigned long printTime = millis();
    static float pHValue, pHVoltage;

    // Read JSON commands from RPi and parse them
    while (Serial.available()) {
        char symbol = (char)Serial.read();
        if (symbol == '}') {
            commandStr += symbol;
            readJson(commandStr);
        } else {
            commandStr += symbol;
        }
    }

    // Measure pH and TDS every 20 ms
    if (millis() - samplingTime > SAMPLE_TIME) {
        // pH read
        pHArray[pHArrayIndex++] = analogRead(PH_PIN);
        if (pHArrayIndex == PH_ARR_LEN) {
            pHArrayIndex = 0;
        }
        pHVoltage = trimmedMean(pHArray, PH_ARR_LEN) * (float)VREF / 1023.0;
        pHValue = aCoeff * pHVoltage + bCoeff;
        if (pHValue > 14.0) {
            pHValue = 14.0;
        } else if (pHValue < 0) {
            pHValue = 0;
        }
        // TDS read the analog value and store into the buffer
        tdsBuffer[tdsBufferIndex] = analogRead(TDS_PIN);
        tdsBufferIndex++;
        if (tdsBufferIndex == TDS_ARR_LEN) {
            tdsBufferIndex = 0;
        }
        samplingTime = millis();
    }

    // Every 2 seconds, send a data for RPi to Serial port
    if (millis() - printTime > PRINT_TIME) {
        // Read and save current time, date and day of week
        clock.read();
        clock.getTimeStamp(time, date, weekDay);

        // Lamp ON at 6:00 and OFF at 00:00 or at 18:00
        if ((clock.getHour() > LAMP_ON_TIME) && (clock.getHour() < (LAMP_ON_TIME + lampState)) && lampOn) {
            digitalWrite(LAMP_PIN, HIGH);
        } else {
            digitalWrite(LAMP_PIN, LOW);
        }

        // Water Level
        if (digitalRead(LVL_PIN)) {
            lvlState = 1;
        } else {
            lvlState = 0;
        }

        // TDS out
        for (byte i = 0; i < TDS_ARR_LEN; i++) {
            tdsBufferTemp[i] = tdsBuffer[i];
        }
        // Read the analog value more stable by the median filtering algorithm, and convert to voltage value
        averageVoltage = getMedianNum(tdsBufferTemp, TDS_ARR_LEN) * (float)VREF / 1023.0;
        // Temperature compensation: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
        float compensateCoeff = 1.0 + 0.02 * (temperature - 25.0);
        float compensateVoltage = averageVoltage / compensateCoeff;
        // Convert voltage value to TDS value
        tdsValue = (133.42 * compensateVoltage * compensateVoltage * compensateVoltage - 255.86 * compensateVoltage * compensateVoltage + 857.39 * compensateVoltage) * 0.5;

        // ds18b20
        tempSensor.requestTemperatures();
        // CO2
        ccs.readData();
        // Print all data to RPi
        Serial.println("{ \"temp\" : " + String(tempSensor.getTempCByIndex(0)) + ", \"acid\" : " + String(pHValue) + ", \"salin\" : " + String(tdsValue) + ", \"carb\" : " + String(ccs.geteCO2()) + ", \"level\" : " + String(lvlState) + ", \"lmp\" : " + String(lampOn) + ", \"lmpMd\" : " + String(lampState) + ", \"fan\" : " + String(fanOn) + ", \"fanMd\" : " + String(fanTime) + ", \"compr\" : " + String(compressorOn) + ", \"time\" : " + String(clock.getUnixTime()) + " }");

        printTime = millis();
    }
}
// sort array and return median number of array "bArray" with "iFilterLen" of members
int getMedianNum(int bArray[], int iFilterLen) {
    int bTab[iFilterLen];
    for (byte i = 0; i < iFilterLen; i++) {
        bTab[i] = bArray[i];
    }
    int i, j, bTemp;
    for (j = 0; j < iFilterLen - 1; j++) {
        for (i = 0; i < iFilterLen - j - 1; i++) {
            if (bTab[i] > bTab[i + 1]) {
                bTemp = bTab[i];
                bTab[i] = bTab[i + 1];
                bTab[i + 1] = bTemp;
            }
        }
    }
    if ((iFilterLen & 1) > 0) {
        bTemp = bTab[(iFilterLen - 1) / 2];
    } else {
        bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
    }
    return bTemp;
}
// calculate and return trimmed mean of array "arr" with "number" of members
double trimmedMean(int* arr, int number) {
    int i;
    int max, min;
    double avg;
    long amount = 0;
    if (number <= 0) {
        return 0;
    }
    if (number < 5) { //less than 5, calculated directly statistics
        for (i = 0; i < number; i++) {
            amount += arr[i];
        }
        avg = amount / number;
        return avg;
    } else {
        if (arr[0] < arr[1]) {
            min = arr[0];
            max = arr[1];
        } else {
            min = arr[1];
            max = arr[0];
        }
        for (i = 2; i < number; i++) {
            if (arr[i] < min) {
                amount += min; //arr<min
                min = arr[i];
            } else {
                if (arr[i] > max) {
                    amount += max; //arr>max
                    max = arr[i];
                } else {
                    amount += arr[i]; //min<=arr<=max
                }
            } //if
        } //for
        avg = (double)amount / (number - 2);
    } //if
    return avg;
}

// JSON parsing function for commands from Raspberry
void readJson(String param) {
    StaticJsonDocument<200> doc;
    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, param);
    if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.c_str());
        commandStr = "";
        return;
    }
    // Get the root object in the document
    JsonObject root = doc.as<JsonObject>();
    if (root.containsKey("lamp")) {
        lampOn = root["lamp"][0];
        lampState = root["lamp"][1];
    }
    if (root.containsKey("fan")) {
        fanOn = root["fan"][0];
        fanTime = root["fan"][1];
        fanState = true;
        lastFanTime = millis();
    }
    if (root.containsKey("compressor")) {
        compressorOn = root["compressor"];
    }
    if (root.containsKey("setTime")) {
        clock.set(root["setTime"]);
    }
    if (root.containsKey("calibrate")) {
        calibratePH(root["calibrate"]);
    }
    commandStr = "";
}

// pH sensor calibration function
void calibratePH(int calibratePoint) {
    if (calibratePoint == 4) {
        accFour = analogRead(PH_PIN);
    }
    if (calibratePoint == 7) {
        accSeven = analogRead(PH_PIN);
    }
    if ((accFour != 0) && (accSeven != 0)) {
        float accA = (float)3.0 / (((accSeven - accFour) * 5.0) / 1023.0);
        float accB = (float)4.01 - accA * (accFour * 5.0 / 1023.0);
        EEPROM.put(EEPROM_ADDR, accA);
        EEPROM.put(EEPROM_ADDR + 50, accB);
        aCoeff = accA;
        bCoeff = accB;
        accFour = 0;
        accSeven = 0;
    }
}
