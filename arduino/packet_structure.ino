#define headerSize 5
#define samplingTime 4.0/30
//#define samplingTime 4.0/300 

int switching_pin = 13;
int state = 0;
int counterHeader = 0;
int counterByte = 0;
unsigned int data = 0;




void setup() {
  // put your setup code here, to run once:
  pinMode(switching_pin, OUTPUT);
  digitalWrite(switching_pin,0);
  Serial.begin(9600);
  Serial.println("\nBegin:");
}

void loop() {

  //read sensor data 
  data = data;
  
  //Action
  switch(state){
    case 0: //header
      digitalWrite(switching_pin,1);
      Serial.print("H");
      counterHeader++;

      if(counterHeader>=headerSize){
        counterHeader=0;
        state=1;
      }
      
      break;
      
    case 1: //send first 0
      digitalWrite(switching_pin,0);
      Serial.print("L");
      state=2;
      break;
      
    case 2: //send first subByte
      digitalWrite(switching_pin,(data<<counterByte)&0b10000000);
      Serial.print(((data<<counterByte)&0b10000000)>>7);
      counterByte++;

      if(counterByte>=4){
        state=3;
      }
      
      break;
    case 3: //send second 0
      digitalWrite(switching_pin,0);
      Serial.print("L");
      state=4;
      break;
    case 4: //send second subByte
      digitalWrite(switching_pin,(data<<counterByte)&0b10000000);
      Serial.print(((data<<counterByte)&0b10000000)>>7);
      counterByte++;

      if(counterByte>=8){
        counterByte=0;
        state=0;
        Serial.println("");
        if(data++>=256) data=0;
      }
            
      break;
    default:
      break;
  }

  delay(samplingTime*1000);


}
