#include <TroykaMeteoSensor.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_CCS811.h>

//LVL 
#define lvlPin 7
//ph
#define SensorPin A1            //pH meter Analog output to Arduino Analog Input 0
#define Offset 0.00            //deviation compensate
#define ArrayLenth  40    //times of collection
//tds
#define TdsSensorPin A0
#define VREF 5.0      // analog reference voltage(Volt) of the ADC
#define SCOUNT  30           // sum of sample point
//time
#define printInterval 2000
#define samplingInterval 20
//ds18b20
#define ONE_WIRE_BUS 11

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

//meteosensor
TroykaMeteoSensor meteoSensor;
//ds18b20
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

//co2
Adafruit_CCS811 ccs;

void setup(void) {
  pinMode(5,OUTPUT);
  digitalWrite(5,LOW);
  meteoSensor.begin();
  Serial.begin(9600);
  pinMode(TdsSensorPin, INPUT);
  sensors.begin();
  ccs.begin();
  while (!ccs.available());
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 25.0);
}

void loop(void) {
  static unsigned long samplingTime = millis();
  static unsigned long printTime = millis();
  static float pHValue, voltage;

  if (millis() - samplingTime > samplingInterval) {
    //ph read
    pHArray[pHArrayIndex++] = analogRead(SensorPin);
    if (pHArrayIndex == ArrayLenth) {
      pHArrayIndex = 0;
    }
    voltage = averageArray(pHArray, ArrayLenth) * 5.0 / 1024;
    pHValue = 3.5 * voltage + Offset;
    samplingTime = millis();
    //tds read
    analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);    //read the analog value and store into the buffer
    analogBufferIndex++;
    if (analogBufferIndex == SCOUNT) {
      analogBufferIndex = 0;
    }
  }

  //Every 800 milliseconds, print a numerical, convert the state of the LED indicator
  if (millis() - printTime > printInterval) {
    //lvl
    if (digitalRead(lvlPin)) {
      lvlState = 1;
    } else {
      lvlState = 0;
    }
   // Serial.print(lvlState);
   // Serial.print("\t");

    // meteosensor
    int stateSensor = meteoSensor.read();

//        Serial.print("TempAir = ");
//        Serial.print(meteoSensor.getTemperatureC());
//        Serial.print(" C \t");
//        Serial.print("Humidity = ");
//        Serial.print(meteoSensor.getHumidity());
//        Serial.print(" %\t");

    // tds out
    for (copyIndex = 0; copyIndex < SCOUNT; copyIndex++) {
      analogBufferTemp[copyIndex] = analogBuffer[copyIndex];
    }
    averageVoltage = getMedianNum(analogBufferTemp, SCOUNT) * (float)VREF / 1024.0; // read the analog value more stable by the median filtering algorithm, and convert to voltage value
    float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0); //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
    float compensationVolatge = averageVoltage / compensationCoefficient; //temperature compensation
    tdsValue = (133.42 * compensationVolatge * compensationVolatge * compensationVolatge - 255.86 * compensationVolatge * compensationVolatge + 857.39 * compensationVolatge) * 0.5; //convert voltage value to tds value
    //Serial.print("voltage:");
    //Serial.print(averageVoltage,2);
    //Serial.print("V   ");
    //Serial.print("TDS Value:");
    //Serial.print(tdsValue, 0);
    //Serial.print("ppm \t");

    //hp out
    //Serial.print("pH value: ");
    //Serial.print(pHValue, 2);
    //Serial.print(" \t");
    
    // ds18b20
    sensors.requestTemperatures();
//    Serial.print("TempWater= ");
//    Serial.print(sensors.getTempCByIndex(0));
//    Serial.print(" C \t");

    //co2
    ccs.readData();
    //Serial.print("eCO2: ");                                 // Значение уровня eCO2
    //Serial.print(ccs.geteCO2());
    //Serial.println("ppm ");                                 // Значение уровня TVOC
    //String(meteoSensor.getTemperatureC());
    Serial.println(String(sensors.getTempCByIndex(0))+" "+String(meteoSensor.getHumidity())+" "+String(pHValue)+" "+String(tdsValue)+" "+String(ccs.geteCO2())+" "+String(lvlState));
    printTime = millis();
  }
}

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

double averageArray(int* arr, int number) {
  int i;
  int max, min;
  double avg;
  long amount = 0;
  if (number <= 0) {
    Serial.println("Error number for the array to avraging!/n");
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
    } else {
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
