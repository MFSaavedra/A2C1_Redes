# Pruebas

Salida de las siete pruebas del enunciado (4 de funcionalidad y 3 experimentos),
ejecutadas el 2026-09-02 con el resolver corriendo en la máquina virtual
(`IP_VM` = 192.168.2.5, puerto UDP 8000) y `dig` desde el host, 192.168.2.4.

Cada archivo trae la salida de `dig` en el cliente y la del modo debug en la VM.
El resolver se reinició antes de cada prueba, así que todas parten con el caché
vacío. En la salida del resolver se omitieron los volcados de bytes y la
estructura parseada, marcados con `[... omitido ...]`; el resto es literal.

| Archivo | Prueba |
|---|---|
| `1-eol-uchile.txt` | Funcionalidad 1: `eol.uchile.cl` |
| `2-cache-eol-uchile.txt` | Funcionalidad 2: la repetición la responde el caché |
| `3-www-uchile.txt` | Funcionalidad 3: `www.uchile.cl` |
| `4-cc4303-bachmann.txt` | Funcionalidad 4: `cc4303.bachmann.cl` |
| `5-exp1-webofscience.txt` | Experimento 1: `www.webofscience.com` |
| `6-exp2-www-cc4303.txt` | Experimento 2: `www.cc4303.bachmann.cl` |
| `7-exp3-name-servers.txt` | Experimento 3: cinco resoluciones del mismo dominio |
