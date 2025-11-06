Estos es un juego simulando al sonic retro, proximamente con sprite hechos propiamente.
Arduino IDE 
// Arduino | Joysticks + Botones
const int joyX = A0;       // Pin analógico para eje X
const int joyY = A1;       // Pin analógico para eje Y
const int jumpButton = 4;  // Pin digital D4 para el pulsador de salto
const int menuButton = 5;  // Pin digital D5 para el pulsador de menú
const int runButton = 6; // Pin digital D6 para el pulsador de correr

void setup() {
  Serial.begin(9600);  // Iniciar comunicación serial
  pinMode(jumpButton, INPUT_PULLUP); // Configurar D4 con resistencia pull-up interna
  pinMode(menuButton, INPUT_PULLUP); // Configurar D5 con resistencia pull-up interna
  pinMode(runButton, INPUT_PULLUP); // cONFIGURAR D6 con resistencia pull-up interna
}

void loop() {
  int xValue = analogRead(joyX);          // Leer eje X (0-1023)
  int yValue = analogRead(joyY);          // Leer eje Y (0-1023)
  int buttonJump = digitalRead(jumpButton); // Leer pulsador de salto (0=presionado)
  int buttonMenu = digitalRead(menuButton); // Leer pulsador de menú (0=presionado)
  int buttonrun = digitalRead(runButton);

  // Enviar los cuatro valores por serial separados por comas
  Serial.print(xValue);
  Serial.print(",");
  Serial.print(yValue);
  Serial.print(",");
  Serial.print(buttonJump);
  Serial.print(",");
  Serial.print(buttonMenu);
  Serial.print(",");
  Serial.println(buttonrun);

  delay(50); // Pequeña pausa para estabilidad
}Arduino IDE 
// Arduino | Joysticks + Botones
const int joyX = A0;       // Pin analógico para eje X
const int joyY = A1;       // Pin analógico para eje Y
const int jumpButton = 4;  // Pin digital D4 para el pulsador de salto
const int menuButton = 5;  // Pin digital D5 para el pulsador de menú
const int runButton = 6; // Pin digital D6 para el pulsador de correr

void setup() {
  Serial.begin(9600);  // Iniciar comunicación serial
  pinMode(jumpButton, INPUT_PULLUP); // Configurar D4 con resistencia pull-up interna
  pinMode(menuButton, INPUT_PULLUP); // Configurar D5 con resistencia pull-up interna
  pinMode(runButton, INPUT_PULLUP); // cONFIGURAR D6 con resistencia pull-up interna
}

void loop() {
  int xValue = analogRead(joyX);          // Leer eje X (0-1023)
  int yValue = analogRead(joyY);          // Leer eje Y (0-1023)
  int buttonJump = digitalRead(jumpButton); // Leer pulsador de salto (0=presionado)
  int buttonMenu = digitalRead(menuButton); // Leer pulsador de menú (0=presionado)
  int buttonrun = digitalRead(runButton);

  // Enviar los cuatro valores por serial separados por comas
  Serial.print(xValue);
  Serial.print(",");
  Serial.print(yValue);
  Serial.print(",");
  Serial.print(buttonJump);
  Serial.print(",");
  Serial.print(buttonMenu);
  Serial.print(",");
  Serial.println(buttonrun);

  delay(50); // Pequeña pausa para estabilidad
}