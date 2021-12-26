docker run -d \
  -p 5000:5000 \
  --restart=always \
  --name registry \
  -v /mnt/registry:/var/lib/registry \
  registry:2
  
  
  docker run -d \
  --restart=always \
  --name registry \
  -v "$(pwd)"/certs:/certs \
  -v /mnt/registry:/var/lib/registry \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:10443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/satis-applications.com.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/satis-applications.com.key \
  -p 10443:10443 \
  registry:2
  
  
  
  
  welche sind mit LAN? 


[L]Raspberry pi 1: Richard Rudek
[L]Raspberry pi 2: 
[L]Raspberry pi 3: Mohamed Ali
[L]Raspberry pi 4: Henk Lubig
Raspberry pi 5: Dennis Kuna
Raspberry pi 6: Florian Schott
Raspberry pi 7:
Raspberry pi 8: Stefan Sadewasser 
Raspberry pi 9: Mark Morgan
Raspberry pi 10: Simon Breiter
Raspberry pi 11: Aiman Ibrahim Abdou
Raspberry pi 12: Enrico de Chadarevian
[L]Raspberry pi 13: Davis Frank
Raspberry pi 14: Marcel Lorenz
[L]Raspberry pi 15: Philipp Schach
[L]Raspberry pi 16: Conrad Kirschner 
[L]Raspberry pi 20: Suhieb Al-Khatib


                                                   
                        
                                
                                        
[LoRa Config] 
                                        
AT+CFG=433000000,20,9,12,4,1,0,0,0,0,3000,8,4 
                                        
[Links]
- Readme Generator https://readme.so/editor 
                                        
- RFC Ad hoc On-Demand Distance Vector (AODV) Routing 
                                        
https://datatracker.ietf.org/doc/html/rfc3561 
                                        
- Datasheet für Seriale commands 
                                        
https://ecksteinimg.de/Datasheet/HIMO-01(M)user%20menu%20V0.6(en).pdf 
                                        
[Serial Config] 
                                        
baudRate=115200 parity=0 flowControl=0 numberOfStopBits=1 numberOfDataBits=8 
                                        
[How to Connect] 
                                        
ssh -X user@gridgateway.f4.htw-berlin.de (WLAN) ssh -X pi@10.10.10.133
(LAN) ssh -X pi@10.10.10.33 
                                
                        
                                                                                           
                
                        
                                
                                        
pw: 1Himbeere 
                                
                        
                        
                                
                                        
[Schema für IP-Adresse der Pis] 
                                        
Raspi 1 -> ...131
...
Raspi 13 -> ...143
Raspi 20 -> ...150
Kabel adresse z.b. 1xx(wlan) => 0xx (lan) 
                                        
-> ( bzw ohne 0 ) <- 10.10.10.31 
                                        
[Raspi config] 
                                        
Befehlsübersicht
AT
AT+RST
AT+VER
AT+RX
AT+ADDR=00xx
AT+ADDR?
AT+DEST=FFFF
AT+DEST? AT+CFG=433000000,20,7,12,4,1,0,0,0,0,3000,8,4 
                                        
Start AT+CFG=433000000,20,7,12,4,1,0,0,0,0,3000,8,4 AT+ADDR?
AT+ADDR=000X (Modulnummer) 
                                        
z.B. Modellnummer 7 = 0007 AT+DEST? -> FFFF 
                                        
AT+RX AT+SEND=5 Hallo 
                                        
[Messungen] 
                                        
Test 1 - Max 5 Bytes (Sender: 9)
(geringe Sendeleistung, ?) AT+CFG=433000000,5,4,12,4,1,0,0,0,0,3000,8,4 empfangen von: 3, 11 ( not sure - ?) <--- ergänzen 
                                        
Test 2 - Max 5 Bytes (Sender: 9)
(geringe Sendeleistung, ?) AT+CFG=433000000,5,4,12,4,1,0,0,0,0,3000,8,4 empfangen von: 3, 11 ( not sure - ?) <--- ergänzen 
                                        
https://cryptpad.fr/sheet/#/2/sheet/edit/eG87V5X8ixHZexswgLPG6gfI/ 
                                        
[Socat] 
                                        
// Was ist das? // 
                                        
Socat is a command line based utility that establishes two bidirectional byte streams and transfers data between them.
---------- Code --------- 
                                
                        
                        
                                
                                        
- Testbefehl - Reset 
                                
                        
                        
                                
                                        
- Versionsanzeige
- Empfangsmodus aktivieren AT+ADDR={Adresse} 
                                
                        
                        
                                
                                        
- Eigene Adresse setzen
- Eigene Adresse abfragen 
                                
                        
                        
                                
                                        
- Zieladresse setzen - Zieladresse abfragen 
                                
                        
                                         
                
                        
                                
                                        
# 
                                                                                         

                                                            

    #  & means run in background 

                                                    

                                                    

                                                            

    #  change jobs (foreground and background) 

                                                    

                                                    

                                                            

    #  with fg (foreground) and bg (background) # 

                                                    

                                                    

                                                            

    #  connect

    sudo socat -v -d -d PTY,link=/dev/ttyAMA0 PTY,link=/dev/ttyS0 & 

                                                            

    # change owner to pi from AMA0 sudo chown -c pi /dev/ttyAMA0 

                                                            

    # change owner to pi from ttyS0 sudo chown -c pi /dev/ttyS0 

                                                            

    ----- Alternativ --------

    sudo socat -v -d -d PTY,link=/dev/ttyAMA0 PTY,link=/dev/ttyS0 & sudo chown -c pi /dev/ttyAMA0

    sudo chown -c pi /dev/ttyS0

    cutecom &

    cutecom &

    (Zur Gui wechseln und auswählen[AMA0/ttyS0])

    ----- Code end -------- 

                                                            

    [FAQ] 

                                                            

    1. Permission Denied 

                                                            

    cd /dev

    ls

    cutecom &

    (In cutecom Permission denied)

    sudo chown -c pi /dev/ttyS0

    sudo chown -c pi /dev/ttyAMA0

    Grund: Beim starten von socat werden 2 neue virtuelle devices generiert, daher sind die permissions immer auf root gesetzt 

                                                            

    2. Could not connect to any X-Display. 

                                                            

    Windows: Xlaunch (evtl. oder linux vm)

    Ubuntu Linux (wenn nicht vorinstalliert): https://askubuntu.com/questions/213678/how-to-install-x11-xorg $ sudo apt-get install xorg openbox

    Mac: --- 

                                                            

    3. Permission Denied v2

    cd /dev

    ls

    sudo socat -v -d -d PTY,link=/dev/AMA0 PTY,link=/dev/S0

    (Hostname kann nicht aufgelöst werden: Der Name oder der Dienst ist nicht bekannt) ls 

                                                            

    sudo socat -v -d -d PTY,link=/dev/ttyAMA0 PTY,link=/dev/ttyS0 sudo chown -c pi /dev/ttyS0

    sudo chown -c pi /dev/ttyAMA0

    Grund: Ohne tty wird keine Verknüpfung erstellt? 

                                                    

                                          

                                
                                        
4. Wie starte ich Cutecom in mehreren Fenstern im selben Terminal                         
                                        
cutecom & (1. Fenster) cutecom & (2. Fenster) 
                                        
5. Pseudoterminals werden nicht erkannt von Cutecom, deswegen AMA0 / S0
6. [PYTHON] Linefeed ending missing -> endless sending \r\n (encoding?) oder als bytes irgendwie ? => 
                                        
7. Unterschied zwischen HTOP und TOP HTOP ist verbessertes TOP
eher htop verwenden! 
                                        
8. Wie kann ich das LoRa Modul resetten? GPIO18 -> HW Reset Lora Modul
=> LOW 
                                        
9. Wie kann ich eine Datei via ssh auf den Pi kopieren? 
                                        
SCP tunneln:
scp -o 'ProxyCommand ssh userB@hostB nc %h %p' infile.txt userC@hostC:"~/outfile.txt" 
                                        
WinSCP (scp: https://gridscale.io/community/tutorials/scp-linux-windows/ ) 
                                        
10. Wofür steht AT und LR? 
                                        
https://de.wikipedia.org/wiki/AT-Befehlssatz https://wireless-solutions.de/downloadfile/lr-base-documents/ (AT base und LR Base) 
                                        
[Protokol - Hello my neigbours] 
                                        
1. "Hello" senden alle 5 Sekunden, alle x Sekunden (x = wechselnd, nicht fest) 2. speichern von wem habe ich "Hello" Empfangen 
                                        
[Ziel: Wir finden ein besseres Chat Protokoll als dieses Projekt!] 
                                        
https://github.com/linuxluigi/PyLoRaWebChat 
