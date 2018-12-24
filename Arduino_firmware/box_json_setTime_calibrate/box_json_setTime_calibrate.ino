//#include <TroykaMeteoSensor.h>
#include <Wire.h>
#include "OneWire.h"
#include "DallasTemperature.h"
#include "Adafruit_CCS811.h"
#include "ArduinoJson.h"
#include "TroykaRTC.h"
#include <EEPROM.h>
#define eeAddr 0
#define lampPin  8
#define compressorPin 9
#define fanPin 10
//LVL
#define lvlPin 7
//ph
#define SensorPin A3            //pH meter Analog output to Arduino Analog Input 0
#define Offset 0.00            //deviation compensate
#define ArrayLenth  40    //times of collection
//tds
#define TdsSensorPin A2
#define VREF 5.0      // analog reference voltage(Volt) of the ADC
#define SCOUNT  30           // sum of sample point
//time
#define printInterval 2000
#define samplingInterval 20
//ds18b20
#define ONE_WIRE_BUS 6
// размер массива для времени
#define LEN_TIME 12
// размер массива для даты
#define LEN_DATE 12
// размер массива для дня недели
#define LEN_DOW 12
//ph
int pHArray[ArrayLenth];   //Store the average value of the sensor feedback
int pHArrayIndex = 0;

//LVL
int lvlState = 0;

//tds
int analogBuffer[SCOUNT];    // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0, copyIndex = 0;
float averageVoltage = 0, tdsValue = 0, temperature = 25;
float akoff,bkoff = 0;
//meteosensor
//TroykaMeteoSensor meteoSensor;
//ds18b20
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

//co2
Adafruit_CCS811 ccs;
RTC clock;

// массив для хранения текущего времени
char time[LEN_TIME];
// массив для хранения текущей даты
char date[LEN_DATE];
// массив для хранения текущего дня недели
char weekDay[LEN_DOW];
int lampState = 0;
int lampOn = 0;
int compressorOn = 0;
int fanOn = 0;
float fanState = 0;
long lastFanTime = 0;
String strRq = "";
float accFour = 0;
float accSeven = 0;
void setup(void)
{
  EEPROM.get(eeAddr,akoff);
  EEPROM.get(eeAddr+50,bkoff);
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);
  //meteoSensor.begin();
  Serial.begin(9600);
  pinMode(TdsSensorPin, INPUT);
  sensors.begin();
  ccs.begin();
  while (!ccs.available());
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 25.0);
  lastFanTime = millis();
  pinMode(lampPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(compressorPin, OUTPUT);
  clock.begin();

}

void loop(void)
{
  if (compressorOn) {
    digitalWrite(compressorPin, HIGH);
  } else {
    digitalWrite(compressorPin, LOW);
  }
  if (fanOn && ((millis() - lastFanTime) > fanState * 60000)) {
    digitalWrite(fanPin, HIGH);
    if ((millis() - lastFanTime) > 120000 * fanState) {
      lastFanTime = millis();
    }
  } else {
    digitalWrite(fanPin, LOW);
  }



  static unsigned long samplingTime = millis();
  static unsigned long printTime = millis();
  static float pHValue, voltage;
  while (Serial.available()) {
    char symbol = (char)Serial.read();
    if (symbol == '}') {
      strRq += symbol;
      readJson(strRq);
    } else {
      strRq += symbol;
    }
  }


  if (millis() - samplingTime > samplingInterval)
  {
    //ph read
    pHArray[pHArrayIndex++] = analogRead(SensorPin);
    if (pHArrayIndex == ArrayLenth)pHArrayIndex = 0;
    voltage = avergearray(pHArray, ArrayLenth) * 5.0 / 1024;
    pHValue = akoff * voltage + bkoff;
    samplingTime = millis();
    //tds read
    analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);    //read the analog value and store into the buffer
    analogBufferIndex++;
    if (analogBufferIndex == SCOUNT)
      analogBufferIndex = 0;

  }





  if (millis() - printTime > printInterval)  //Every 800 milliseconds, print a numerical, convert the state of the LED indicator
  {
    clock.read();
    // сохраняем текущее время, дату и день недели в переменные
    clock.getTimeStamp(time, date, weekDay);
    //Serial.println(clock.getHour());
    if ((clock.getHour() > 5) & (clock.getHour() < (5 + lampState))&lampOn) {
      digitalWrite(lampPin, HIGH);
    } else {
      digitalWrite(lampPin, LOW);
    }

    //lvl
    if (digitalRead(lvlPin)) {
      lvlState = 1;
    } else {
      lvlState = 0;
    }
    // Serial.print(lvlState);
    // Serial.print("\t");

    // meteosensor
    //    int stateSensor = meteoSensor.read();


    //        Serial.print("TempAir = ");
    //        Serial.print(meteoSensor.getTemperatureC());
    //        Serial.print(" C \t");
    //        Serial.print("Humidity = ");
    //        Serial.print(meteoSensor.getHumidity());
    //        Serial.print(" %\t");



    // tds out
    for (copyIndex = 0; copyIndex < SCOUNT; copyIndex++)
      analogBufferTemp[copyIndex] = analogBuffer[copyIndex];
    averageVoltage = getMedianNum(analogBufferTemp, SCOUNT) * (float)VREF / 1024.0; // read the analog value more stable by the median filtering algorithm, and convert to voltage value
    float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0); //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
    float compensationVolatge = averageVoltage / compensationCoefficient; //temperature compensation
    tdsValue = (133.42 * compensationVolatge * compensationVolatge * compensationVolatge - 255.86 * compensationVolatge * compensationVolatge + 857.39 * compensationVolatge) * 0.5; //convert voltage value to tds value
    //Serial.print("voltage:");
    //Serial.print(averageVoltage,2);
    //Serial.print("V   ");
    //    Serial.print("TDS Value:");
    //    Serial.print(tdsValue, 0);
    //    Serial.print("ppm \t");

    //hp out
    //    Serial.print("pH value: ");
    //    Serial.print(pHValue, 2);
    //    Serial.print(" \t");


    // ds18b20
    sensors.requestTemperatures();
    //    Serial.print("TempWater= ");
    //    Serial.print(sensors.getTempCByIndex(0));
    //    Serial.print(" C \t");

    //co2
    ccs.readData();
    //    Serial.print("eCO2: ");                                              // Значение уровня eCO2
    //    Serial.print(ccs.geteCO2());
    //    Serial.println("ppm ");                                        // Значение уровня TVOC
    //String(meteoSensor.getTemperatureC())
    Serial.println("{ \"temp\" : " + String(sensors.getTempCByIndex(0)) + ", \"acid\" : " + String(pHValue) + ", \"salin\" : " + String(tdsValue)
                   + ", \"carb\" : " + String(ccs.geteCO2()) + ", \"level\" : " + String(lvlState) + ", \"lmp\" : " + String(lampOn) + ", \"lmpMd\" : " + String(lampState)
                   + ", \"fan\" : " + String(fanOn) + ", \"fanMd\" : " + String(fanState) + ", \"copmr\" : " + String(compressorOn) + ", \"time\" : " + String(clock.getUnixTime()) + " }");
    printTime = millis();

  }
}



int getMedianNum(int bArray[], int iFilterLen)
{
  int bTab[iFilterLen];
  for (byte i = 0; i < iFilterLen; i++)
    bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++)
  {
    for (i = 0; i < iFilterLen - j - 1; i++)
    {
      if (bTab[i] > bTab[i + 1])
      {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0)
    bTemp = bTab[(iFilterLen - 1) / 2];
  else
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  return bTemp;
}








double avergearray(int* arr, int number) {
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
      min = arr[0]; max = arr[1];
    }
    else {
      min = arr[1]; max = arr[0];
    }
    for (i = 2; i < number; i++) {
      if (arr[i] < min) {
        amount += min;      //arr<min
        min = arr[i];
      } else {
        if (arr[i] > max) {
          amount += max;  //arr>max
          max = arr[i];
        } else {
          amount += arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount / (number - 2);
  }//if
  return avg;
}

void readJson(String param) {
  // Use arduinojson.org/assistant to compute the capacity.
  StaticJsonDocument<200> doc;

  // StaticJsonDocument<N> allocates memory on the stack, it can be
  // replaced by DynamicJsonObject which allocates in the heap.
  //
  // DynamicJsonObject doc(200);

  // JSON input string.
  //
  // It's better to use a char[] as shown here.
  // If you use a const char* or a String, ArduinoJson will
  // have to make a copy of the input in the JsonBuffer.

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, param);

  // Test if parsing succeeds.
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.c_str());
    strRq = "";
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
    fanState = root["fan"][1];
    lastFanTime = millis() - fanState * 60000;
  }
  if (root.containsKey("compressor")) {
    compressorOn = root["compressor"];
  }
  if (root.containsKey("setTime")){
    clock.set(root["setTime"]);
  }
  if (root.containsKey("calibrate")){
    calibratePH(root["calibrate"]);
  }
  strRq = "";
}


void calibratePH(int x){
  if(x == 4){
    accFour = analogRead(SensorPin);
    //Serial.println(accFour); //TODO!
  }
  if(x == 7){
    accSeven = analogRead(SensorPin);
    //Serial.println(accSeven); //TODO!
  }
  if ((accFour != 0) && (accSeven != 0)){
    float accA = (float)3.0/(((accSeven - accFour)*5.0)/1024.0);
    float accB = (float)4.01 - accA*(accFour*5.0/1024.0);
    EEPROM.put(eeAddr,accA);
    EEPROM.put(eeAddr+50,accB);
    //Serial.println(accA);
    //Serial.println(accB);
    akoff = accA;
    bkoff = accB;
    accFour = 0;
    accSeven = 0;
  }
  
}
