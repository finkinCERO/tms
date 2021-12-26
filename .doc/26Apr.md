# In progress


AT - Testbefehl 
AT+RST - Reset 
AT+VER - Versionsanzeige 
AT+RX - Empfangsmodus aktivieren AT+ADDR={Adresse} - Eigene Adresse setzen 
AT+ADDR? - Eigene Adresse abfragen AT+DEST={Adresse} - Zieladresse setzen AT+DEST? - Zieladresse abfragen
AT+CFG=433000000,20,7,12,4,1,0,0,0,0,3000,8,4

Start
AT+CFG=433000000,20,7,12,4,1,0,0,0,0,3000,8,4
AT+ADDR?
AT+ADDR=000X (Modulnummer)
AT+DEST? -> FFFF
AT+RX
AT+SEND=5
Hallo

FAQ
GPIO18 -> HW Reset Lora Modul
=> LOW 
AT - Testbefehl 
AT+RST - Reset 
AT+VER - Versionsanzeige 
AT+RX - Empfangsmodus aktivieren AT+ADDR={Adresse} - Eigene Adresse setzen 
AT+ADDR? - Eigene Adresse abfragen AT+DEST={Adresse} - Zieladresse setzen AT+DEST? - Zieladresse abfragen
AT+CFG=433000000,20,7,12,4,1,0,0,0,0,3000,8,4

Start
AT+CFG=433000000,20,7,12,4,1,0,0,0,0,3000,8,4
AT+ADDR?
AT+ADDR=000X (Modulnummer)
AT+DEST? -> FFFF
AT+RX
AT+SEND=5
Hallo

FAQ
GPIO18 -> HW Reset Lora Modul
=> LOW 

Test 1 - Max 5 Bytes (Sender: 9)
(geringe Sendeleistung, ?) 
AT+CFG=433000000,5,4,12,4,1,0,0,0,0,3000,8,4
empfangen von: 3, 11 ( not sure - ?) <--- ergänzen
# ZUGANG

```bash
ssh -X s0000000@gridgateway.f4.htw-berlin.de
ssh -X pi@10.10.10.133
pw: 1Himbeere

```
