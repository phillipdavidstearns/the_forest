import processing.net.*; 

Client c; 
String data;

void setup() { 
  size(200, 200); 
  background(50); 
  fill(200);
  c = new Client(this, "10.79.103.125", 31337);  // Connect to server on port 80 
  c.write("GET / HTTP/1.0\n");  // Use the HTTP "GET" command to ask for a webpage
  c.write("Host: www.ucla.edu\n\n"); // Tell the server for which domain you are making the request
} 

void draw() {
}
