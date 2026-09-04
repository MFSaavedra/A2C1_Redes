# CC4303 — Actividad 2: resolver DNS

Actividad 2 del curso **Redes (CC4303)**, DCC — Universidad de Chile.
El objetivo es implementar un resolver DNS sobre sockets UDP: recibe consultas de
`dig`, resuelve el dominio de forma **iterativa** partiendo desde un servidor raíz,
y devuelve al cliente un mensaje DNS de respuesta.

**Restricción:** solo se permiten la librería estándar de Python y `dnslib`. No se usa
`dnspython` ni ninguna librería de resolución; el envío y la recepción de los mensajes
se hacen con `socket`, y `dnslib` se usa únicamente para parsear y construir los
mensajes DNS.

Integrantes: María Moya G., M. Fernando Saavedra.

## Ramas

| Rama | Contenido |
|---|---|
| `feature/resolver` | Envío de mensajes por UDP, parseo de mensajes DNS y el algoritmo de resolución iterativa (`resolver()`). |
| `feature/debug` | Modo debug: por cada consulta interna imprime el dominio, el servidor consultado y su IP. |
| `feature/cache` | Caché de los 3 dominios más frecuentes entre las últimas 20 consultas, resultados de las pruebas e informe. |
| `main` | Rama por defecto; integra las tres anteriores. |

## Ejecución

```bash
python3 resolver.py
```

Queda escuchando en `0.0.0.0:8000` (en la VM se accede como `IP_VM:8000`). Se usa el
puerto 8000 y no el 53 porque este último es reservado y requiere privilegios de root.
Desde otra terminal, o desde el anfitrión:

```bash
dig -p8000 @IP_VM eol.uchile.cl        # 146.83.63.X
dig -p8000 @IP_VM eol.uchile.cl        # misma IP, respondida por el caché
dig -p8000 @IP_VM www.uchile.cl        # 200.89.76.36
dig -p8000 @IP_VM cc4303.bachmann.cl   # 104.248.65.245
```

El modo debug se controla con la constante `DEBUG` al inicio de `resolver.py`
(activado por defecto).

## Archivos

- **`resolver.py`** — el resolver: la función `resolver()` con el algoritmo iterativo y
  el bucle principal que recibe consultas por UDP, revisa el caché y responde.
- **`utils.py`** — funciones auxiliares: `send_udp_message`, `parse_dns_message` y
  `update_cache`, además del caché mismo.
- **`pruebas/`** — salida de las cuatro pruebas de funcionalidad y los tres experimentos
  del enunciado (ver `pruebas/README.md`).
- **`Informe/`** — informe LaTeX de la actividad (`main.tex`).

## Implementación

### Resolución iterativa

`resolver(mensaje_consulta, ip_addr, ns_name)` recibe la consulta original del cliente
**en bytes** y devuelve un mensaje DNS completo, también en bytes, porque es lo que
`dig` espera. Parte en la raíz (`198.41.0.4`) y en cada paso:

1. Envía la consulta original —sin modificarla— al servidor de turno.
2. Si la sección Answer trae un registro A, devuelve esa respuesta tal cual.
3. Si no, y la sección Authority trae registros NS, busca glue en Additional:
   - si hay un registro A, reenvía la consulta original a esa IP;
   - si no hay glue, toma el nombre de un NS y **llama recursivamente** a `resolver()`
     para averiguar su IP, y recién entonces reenvía la consulta original allí.
4. Cualquier otro caso se ignora y se devuelve una respuesta vacía.

Nótese que la recursión es sobre el *nombre del servidor*, mientras que la consulta del
cliente viaja intacta por toda la cadena de delegación. El diagrama de flujo está en
`Informe/img/algoritmo_resolver.dot`.

### Socket UDP

Se usa `socket.SOCK_DGRAM` porque DNS opera sobre UDP: son mensajes cortos, de una
consulta y una respuesta, donde el costo de establecer una conexión TCP no se justifica.
El buffer de recepción es de 4096 bytes; el truncamiento y el respaldo sobre TCP están
fuera del alcance de la actividad.

### Caché

No es un caché DNS común: guarda los **3 dominios más frecuentes entre las últimas 20
consultas recibidas**. `update_cache` mantiene una lista con esa ventana deslizante,
cuenta las frecuencias con `Counter` y deja en el caché solo a los tres primeros,
eliminando al resto. Se almacena la dirección IP, no el mensaje completo, así que un
acierto de caché se responde reconstruyendo la respuesta sobre la consulta del cliente.
Es en memoria y no considera TTL. Los aciertos y fallos se ven en el modo debug.

## Limitación conocida

El algoritmo solo entiende registros A y NS, y el caso de `www.webofscience.com` muestra
lo que eso cuesta. Su servidor autoritativo responde con dos **CNAME** en Answer y, junto
con ellos, el conjunto NS de la zona en Authority: una respuesta final que tiene la misma
forma que una delegación. Sin registros A en Answer y sin glue en Additional, el resolver
la lee como delegación, resuelve el nombre del NS y le reenvía la consulta al mismo
servidor que acaba de responder, quedando en un ciclo hasta que `dig` corta por timeout.
El arreglo tiene dos partes: seguir el CNAME reiniciando la resolución sobre el nombre
canónico, y cortar la delegación que no avanza cuando la IP de destino se repite o se
supera una profundidad máxima.
