# Universidad de Costa Rica
## `IE1118` - Temas especiales II en sistemas de Potencia.
### Python para Sistemas de Potencia.
#### Cargabilidad de una red de transmisión

Tercer ciclo del 2022

- Mario Roberto Peralta, B75626

---

Otro problema al que se enfrentan los operadores de redes de transmisión es garantizar que la red funcione incluso en condiciones de mucho estrés. ¿Será el sistema capaz de mantener tensiones cerca de las nominales ante aumentos considerables de carga? Dada una perturbación, como la salida de una línea de transmisión o la de un generador, ¿se sobrecargará alguna de las líneas remanentes? ¿Sobrevivirá el sistema siquiera la perturbación?

---

*Planteamiento del problema, Documentación y Resultados del proyecto.*

# Tabla de contenido
1. [Sistema](#1.0) <br>
1. [Asignaciones](#2.0) <br>
1. [Resultados](#3.0) <br>
1. [Referencias](#4.0) <br>

## 1. Sistema Interconectado Nórdico <a class="anchor" id="1.0"></a>
>  Descripción del sistema. <br>

Este sistema está basado en el Sistema Interconectado Nórdico, específicamente en la parte localizada en Suecia. El sistema mostró propensión a la inestabilidad de tensión en la década de los ochentas. Contiene 32 barras de transmisión, 22 de distribución y 20 de generación, para un total de 74 barras. Además, hay 104 ramas, de las cuales 22 son transformadores reductores, 20 son transformadores elevadores y el resto son líneas de transmisión o autotransformadores. Tal y como sucedió en Suecia en los ochentas, la mayoría de la generación se ubica en el norte, mientras que la carga se concentra en la zona central, alrededor de la capital Estocolmo. Las [referencias](#4.0) [1], [2] muestran un diagrama unifilar completo y ciertas simulaciones que lo familiarizan a uno con esta red. El archivo `nordico.txt` contiene todos los datos del sistema.

## 2. Asignaciones <a class="anchor" id="2.0"></a>
> Objetivos <br>

1. Leer el archivo `nordico.txt` y crear un *modelo eléctrico* de la red.
1. Conducir un *estudio de flujos de potencia* y comparar las tensiones calculadas con las presentadas al final del archivo `nordico.txt`.
1. Llevar a cabo un análisis de cargabilidad: escale las cargas consumidas en la zona central —barras 1, 2, 3, 4, 5, 41, 42, 43, 46, 47 y 51— por un mismo parámetro $\lambda > 1$ que aumente en pasos constantes hasta que el cálculo de los flujos de potencia diverja. Grafique las tensiones en por unidad de la zona central en función de todos los $\lambda$ probados.
1. Llevar a cabo un análisis de contingencia: desconectar todas las líneas de transmisión, una a la vez, y determine en cuáles casos el cálculo de flujos de potencia converge y en cuáles no. Explicar a qué podría deberse eso.

## 3. Resultados <a class="anchor" id="3.0"></a>
>  Análisis de resultados obtenidos <br>

## 4. Referencias <a class="anchor" id="4.0"></a>

$[1]$ IEEE Task Force on Test Systems for Voltage Stability and Security Assessment, «Test Systems for Voltage Stability Analysis and Security Assessment,» IEEE, ago. de 2015, págs. 1-161.

$[2]$ T. Van Cutsem, M. Glavic, W. Rosehart y col., «Test Systems for Voltage Stability Studies,» IEEE Transactions on Power Systems, vol. 35, n.o 5, págs. 4078-4087, sep. de 2020. doi: 10.1109/TPWRS.2020.2976834.
