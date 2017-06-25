////////////////////////////////////////////////////////////////////////////////
//                     *** Moving Wall Box Arduino Code ***                   //
//                                                                            //
// This programm should be used together with the MWB controller and an       // 
// Arduino Uno > Rev.3.                                                       //
//									      //
//                            Andreas Genewsky (2015)                         //
//              Max-Planck Institute for Psychiatry, Munich, Germany          //
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// MIT License                                                                //
//                                                                            //   
// Copyright (c) [2015] [Andreas Genewsky]                                    //  
//                                                                            //
// Permission is hereby granted, free of charge, to any person obtaining a    //
// copy of this software and associated documentation files (the "Software"), //
// to deal in the Software without restriction, including without limitation  //
// the rights to use, copy, modify, merge, publish, distribute, sublicense,   //
// and/or sell copies of the Software, and to permit persons to whom the      //
// Software is furnished to do so, subject to the following conditions:       //
//                                                                            //
// The above copyright notice and this permission notice shall be included    //
// in all copies or substantial portions of the Software.                     //
//                                                                            //
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR //
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   //
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    //
// THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER //
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    //
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        //   
// DEALINGS IN THE SOFTWARE.                                                  //
////////////////////////////////////////////////////////////////////////////////

#include <Servo.h> 
#include <EEPROM.h>
#include "EEPROMAnything.h"


#define INPUT_SIZE 4

Servo servoA;
Servo servoB;
int bright = 255;
int dim = 1;
float weightA = 0.0;
float weightB = 0.0;
float weightA_old = 0.0;
float weightB_old = 0.0;
int servoA_cmd = 1;
int servoB_cmd = 1;
int servo_addr = 0;
volatile int running_var = HIGH;
int ledA = 5;
int ledB = 6;
// the following Servo MIN/MAx values have to be determined empirically, 
// and are different for every construction
const int servoA_min = 2148;
const int servoA_max = 949;
const int servoB_min = 958;
const int servoB_max = 2120;
const int backward_increment = 5;
const int forward_increment = 2;

struct config_t
{
   int A;
   int B;
};
struct config_t servo_pos;


void setup()
{
	pinMode(2, INPUT_PULLUP);
	pinMode(3, INPUT_PULLUP);
	pinMode(ledA,OUTPUT);
	pinMode(ledB,OUTPUT);
	analogWrite(ledA, dim);
	analogWrite(ledB, dim);
	pinMode(13, OUTPUT);
	Serial.begin(115200);
	servoA.attach(9);
	servoB.attach(10);
	EEPROM_readAnything(servo_addr,servo_pos);
	servoA.writeMicroseconds(servo_pos.A);
	servoB.writeMicroseconds(servo_pos.B);
}

void loop()
{ 
	weightA = analogRead(A0);
	weightB = analogRead(A1);
	weightA = 0.5*weightA_old +0.5*weightA;
	weightA_old=weightA;
	weightB = 0.5*weightB_old +0.5*weightB;
	weightB_old=weightB;
	weightA = map(weightA, 0, 1023, 1023, 0);
	weightB = map(weightB, 0, 1023, 1023, 0);

	if (digitalRead(2)==LOW){
		running_var = LOW; 
	}

	if (digitalRead(3)==LOW){
		running_var = HIGH; 
	}

// Get next command from Serial (add 1 for final 0)

if (Serial.available() > 0) {
	char input[INPUT_SIZE + 1];
	byte size = Serial.readBytes(input, INPUT_SIZE);
	// Add the final 0 to end the C string
	input[size] = 0;

	// Read each command pair 
	char* command = strtok(input, ":");
	
	if (command != 0) //formerly a while loop
	{
    	// Split the command in two values
    	char* separator = strchr(command, '|');
    	if (separator != 0)
    	{
        	// Actually split the string in 2: replace '|' with 0
        	*separator = 0;
        	servoA_cmd = atoi(command);
        	++separator;
        	servoB_cmd = atoi(separator);
        	if(servoA_cmd == 2){
        	analogWrite(ledA, bright);	
        	analogWrite(ledB, dim);
        	}
        	if(servoB_cmd == 2){
        	analogWrite(ledA, dim);	
        	analogWrite(ledB, bright);
        	}
        	if(servoA_cmd == 0){
        	analogWrite(ledA, dim);	
        	}
        	if(servoB_cmd == 0){
        	analogWrite(ledB, dim);
        	}
        	
    	}
    	// Find the next command in input string
    	command = strtok(0, "&");
	}
}

	if (running_var == HIGH){
		if(servoA_cmd == 0){ 	//A backwwards
			servo_pos.A = servo_pos.A + backward_increment;
		}
		if(servoB_cmd == 0){
			servo_pos.B = servo_pos.B - backward_increment;
		}
		if(servoA_cmd == 2){	//A forwards
			servo_pos.A = servo_pos.A - forward_increment;
		}
		if(servoB_cmd == 2){
			servo_pos.B = servo_pos.B + forward_increment;
		}
	}
	digitalWrite(13,running_var);
	servo_pos.A = constrain(servo_pos.A, servoA_max, servoA_min);	
	servo_pos.B = constrain(servo_pos.B, servoB_min, servoB_max);
	servoA.writeMicroseconds(servo_pos.A); 
	servoB.writeMicroseconds(servo_pos.B); 
	servo_pos.A = servoA.readMicroseconds();
	servo_pos.B = servoB.readMicroseconds();
	EEPROM_writeAnything(servo_addr, servo_pos);

	Serial.print(int(weightA),DEC);
	Serial.print(",");
	Serial.print(int(weightB),DEC);
	Serial.print(",");
	Serial.print(servo_pos.A,DEC);
	Serial.print(",");
	Serial.print(servo_pos.B,DEC);
	Serial.print(",");
	Serial.print("\n");


//The following code allows Python to controll the Arduino!
servoA_cmd = 1;
servoB_cmd = 1;
delay(25);
}


