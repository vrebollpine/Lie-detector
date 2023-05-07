#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>

#include <Adafruit_AHTX0.h>

#include "DFRobot_Heartrate.h"
#define heartratePin A1;
DFRobot_Heartrate heartrate(DIGITAL_MODE); ///< ANALOG_MODE or DIGITAL_MODE

int co2Pin = A0;

#define humdPin A2;

#include <Adafruit_AHTX0.h>

Adafruit_AHTX0 aht;
int average_hr;
int hr_sum;
int num_loop;

int average_co2;
int co2_sum;

int num_anomalies;

int average_humd;
int humd_sum;

void setup() {
// initialize serial communication at 9600 bits per second:
  Serial.begin(115200);

  if (! aht.begin()) {
  Serial.println("Could not find AHT? Check wiring");
  while (1) delay(10);
  }
  Serial.println("AHT10 or AHT20 found");

  pinMode(3, OUTPUT); //green led light
  pinMode(4, OUTPUT); //yellow led light
  pinMode(5, OUTPUT); //red led light
}
void loopFalse(){
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, HIGH); 
}

void loopUncertain(){
  digitalWrite(3, LOW);
  digitalWrite(4, HIGH);
  digitalWrite(5, LOW);
}

void loopTrue(){
  digitalWrite(3, HIGH);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
}
void loop2(){
  if (num_anomalies == 0){
	  loopTrue();
  } 
  else if (num_anomalies == 1){
	  loopUncertain();
  } 
  else if(num_anomalies > 1){
	  loopFalse();
  }
  num_anomalies = 0;
}
// the loop routine runs over and over again forever:
void loop() {

  int heartRate = analogRead(A1);
  heartRate = map(heartRate, 0, 1500, 0, 200);
  Serial.print("Heart rate: ");
  Serial.print(heartRate);

  int co2Value = analogRead(co2Pin); // Read the sensor value
  float voltage = co2Value * (5.0 / 1023.0); // Convert the sensor value to voltage
  float ratio = voltage / 4.9; // Calculate the ratio of the sensor voltage to the reference voltage (4.9V)
  float concentration = (1.67 * pow(ratio, -1.23)) * 1000; // Calculate the concentration of CO2 in ppm
  Serial.print(" CO2 concentration: ");
  Serial.print(concentration);

  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  int humd = humidity.relative_humidity;
  Serial.print(" Humidity: "); 
  Serial.print(humidity.relative_humidity);
  Serial.println("% rH");

  num_loop ++;
  hr_sum += heartRate;
  average_hr = hr_sum /num_loop;

  co2_sum += concentration;
  average_co2 = co2_sum /num_loop;

  humd_sum += humidity.relative_humidity;
  average_humd = humd_sum/num_loop;
  
  
  if (heartRate > average_hr + 30 || heartRate < average_hr-30) {
    num_anomalies++; 
  }
  
  if (concentration > average_co2 +  10000|| concentration < average_co2 -10000) {
	  num_anomalies ++;
  }

  if (humidity.relative_humidity > average_humd + 3 || humidity.relative_humidity < average_humd -3){
    num_anomalies ++; 
  }  
  
  loop2();
  
  delay(1000); // delay in between reads for stability
}

