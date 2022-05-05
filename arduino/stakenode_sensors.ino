#include "DHT.h"

DHT dht(12, DHT11);   

void setup() {
  Wire.begin();
  dht.begin();
  Serial.begin(9600);
}

void loop() {
  float temp_airhum_val[2] = {0};
  if (!dht.readTempAndHumidity(temp_airhum_val)) {
    debug.print("air_humidity(%):");
    debug.print(temp_airhum_val[0]);
    debug.print(",");
    debug.print("temperature(°C):");
    debug.print(temp_airhum_val[1]);
    debug.print(",");
  }
  float soilhum_val = analogRead(A0)/10.23; //percent  
  debug.print("soil_humidity(%):");
  debug.print(soilhum_val);
  debug.println("");
  delay(1500);
}
