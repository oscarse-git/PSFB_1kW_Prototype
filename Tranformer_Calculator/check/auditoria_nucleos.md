# Auditoría independiente: 24 núcleos Magnetics

Fuente: los 24 PDFs de core_database.zip aportado por el usuario. Todos tienen una página. Se revisaron el texto, las tablas y los dibujos renderizados. No se han usado revisiones previas ni fuentes externas. Los valores actuales proceden del vector pegado en el mensaje, no de un archivo Python dentro del ZIP.

## Resultado

No se detectan errores numéricos de transcripción o cálculo bajo las fórmulas solicitadas. Los 168 valores coinciden con sus fuentes o cálculos; 166 campos se verifican sin salvedad específica y 2 quedan cualificados: Aw de 0T42523EC y Ploss de NT41812UG. No procede modificar ningún número. Esto no equivale a certificar 24 núcleos sin reservas: hay 22 sin salvedad específica, uno sin Aw nominal documentado y otro con pérdidas internamente inconsistentes.

## Tabla de discrepancias y reservas

|Referencia|Campo|Valor actual|Valor correcto / contrastado|Estado|
|---|---|---:|---|---|
|0T42523EC|Aw|33.03 mm²|33.03 para D_min × M_nom; nominal no disponible|Reserva: 9.05 mm es mínimo|
|NT41812UG|Ploss|642 mW/cm³|642 publicado; 673.076923 derivado de 0.7 W/set|Fuente inconsistente; conservar 642 según regla solicitada|

## Tabla consolidada de los siete campos

Las unidades son Bmax mT; Ae y Aw mm²; Ve mm³; AL nH/turn²; Ploss mW/cm³. Ae contiene Amin en EC/UG y Ae en TC (no hay Amin en esos TC). En cada fila se verificó también el identificador completo del encabezado, incluidos los guiones.

|id|Bmax|Ae (Amin/Ae)|Aw|Ve|AL|Ploss|
|---|---:|---:|---:|---:|---:|---:|
|0T42019EC|0.5|29|25.02|1460|1540|590|
|0T44444EC|0.5|172|139.27|17800|4640|630|
|0T43939EC|0.5|123|117.15|11500|3650|500|
|0T-44949-EC|0.5|209|171.69|24000|5140|630|
|0T42523EC|0.5|55|33.03|3300|2660|590|
|0T42625UG|0.5|108|42.26|6530|6010|590|
|0T42620UG|0.5|109|30.19|5470|7020|590|
|0T42016UG|0.5|59.1|23.69|2330|4080|590|
|0T45050UG|0.5|314|216.6|37100|9200|630|
|0T43230UG|0.5|142|74.55|12500|6570|630|
|0T44040UG|0.5|175|162.99|20500|6100|629.2682926829268|
|0T41506TC|0.5|11.2|42.66|343|1320|500|
|0T-40603-TC|0.5|4.28|7.31|55.8|1200|520|
|ZT41605TC|0.5|15.6|64.61|580|1580|715|
|ZT42206TC|0.5|25.8|147.41|1395|1790|640|
|ZT43813TC|0.5|114.2|283.53|9462|5190|715|
|ZT44015TC|0.5|138|539.13|14205|5040|610|
|ZT43825TC|0.5|231|283.53|19152|10500|550|
|ZT47313TC|0.5|210|1188.47|34771|4790|880|
|NT42819UG|0.5|89.1|31.93|4310|5500|590|
|NT42316UG|0.5|55.4|23.24|2440|4100|590|
|NT41812UG|0.5|31.2|12.0|1040|2830|642|
|ZT41003TC|0.5|7.3|17.72|151|1330|715|
|0T40601TC|0.5|2|7.31|26.7|592|500|

## Geometría y definición de ventana

- TC: el dibujo identifica B como diámetro interior; se emplea el B de Uncoated Nominal, no el diámetro mínimo recubierto. La ventana circular es πB²/4.
- UG: D es la profundidad de una mitad y 2D la extensión del conjunto. La fórmula exigida D(E−F)/2 reproduce una ventana lateral de una mitad, no toda la ventana de la pareja ensamblada: en el dibujo del conjunto, una abertura tiene extensión 2D y altura (E−F)/2, por lo que su área sería D(E−F). Se conserva estrictamente la convención solicitada; todos los Aw UG actuales son correctos bajo ella. Para dimensionar bobinados debe explicitarse esta convención y evitar confundirla con la abertura completa del conjunto.
- EC grandes: se confirma la profundidad D y la anchura lateral (E−F)/2. Se conserva D(E−F)/2, por mitad y lado.
- 0T42019EC: la cota M=3.25 Ref. mide el espacio lateral del dibujo, y D=7.7 mm la profundidad. D×M=25.025, con np.round da 25.02. Además (15.4−8.9)/2=3.25. Las cotas Ref. son de referencia, no garantizan tolerancia.
- 0T42523EC: el dibujo da M=3.65 ±0.2 mm y D=9.05 Min. D×M=33.0325 → 33.03. No sustituir M por (18.1−11.4)/2=3.35: E=18.1 es también mínima, y el perfil central de este EC es particular. No existe un D nominal numérico en este PDF; 33.03 no puede certificarse como Aw estrictamente nominal ni como mínimo garantizado, pues M también tiene tolerancia. El producto D_min×M_min sería 9.05×3.45=31.2225 mm² como cota rectangular derivada, no el Aw nominal solicitado.

## Pérdidas: contraste W frente a densidad

Se elige siempre la columna individual PL max a 25°C, 100 kHz y 200 mT. En ZT41605TC, ZT42206TC, ZT43813TC, ZT43825TC, ZT47313TC y ZT41003TC se descartó Max avg del lote. En ZT44015TC y varios UG/EC, la fila de 100°C aparece primero: se verificó la temperatura, no el orden. 0T44040UG es el único PDF sin densidad directa: 12.9 W/set × 10⁶ / 20500 mm³ = 629.2682926829268 mW/cm³. No se redondea arbitrariamente a 630.

Las diferencias siguientes son diferencias entre las dos expresiones publicadas del límite; no indican pérdidas medidas. Todas las potencias corresponden a 25°C. La diferencia relativa usa la densidad publicada como denominador.

|Referencia|PL individual W|Ve mm³|Densidad publicada|W×10⁶/Ve|Diferencia %|
|---|---:|---:|---:|---:|---:|
|0T42019EC|0.86|1460|590|589.041096|-0.162526|
|0T44444EC|11.21|17800|630|629.775281|-0.035670|
|0T43939EC|5.75|11500|500|500.000000|0.000000|
|0T-44949-EC|15.12|24000|630|630.000000|0.000000|
|0T42523EC|1.95|3300|590|590.909091|0.154083|
|0T42625UG|3.85|6530|590|589.586524|-0.070081|
|0T42620UG|3.23|5470|590|590.493601|0.083661|
|0T42016UG|1.37|2330|590|587.982833|-0.341893|
|0T45050UG|23.4|37100|630|630.727763|0.115518|
|0T43230UG|7.8|12500|630|624.000000|-0.952381|
|0T44040UG|12.9|20500|No publicada|629.268293|0.000000|
|0T41506TC|0.172|343|500|501.457726|0.291545|
|0T-40603-TC|0.029|55.8|520|519.713262|-0.055142|
|ZT41605TC|0.416|580|715|717.241379|0.313480|
|ZT42206TC|0.892|1395|640|639.426523|-0.089606|
|ZT43813TC|6.76|9462|715|714.436694|-0.078784|
|ZT44015TC|8.665|14205|610|609.996480|-0.000577|
|ZT43825TC|10.54|19152|550|550.334169|0.060758|
|ZT47313TC|30.7|34771|880|882.919674|0.331781|
|NT42819UG|2.54|4310|590|589.327146|-0.114043|
|NT42316UG|1.44|2440|590|590.163934|0.027785|
|NT41812UG|0.7|1040|642|673.076923|4.840642|
|ZT41003TC|0.108|151|715|715.231788|0.032418|
|0T40601TC|0.0134|26.7|500|501.872659|0.374532|

La mayoría de diferencias son pequeñas (menos de 0.8 %) y compatibles con distintas precisiones de publicación/redondeo; no se puede probar sólo con estos PDFs que su causa sea exclusivamente redondeo. No constituyen razón para sustituir la densidad directa por la calculada.

NT41812UG es la excepción material: 0.7 W/set y Ve=1040 implican 673.076923, un 4.8406 % por encima de 642; 642 implica 0.66768 W/set. El dato de 100°C también es inconsistente: 0.58 W/set / 1040 × 10⁶ = 557.692308, frente a 532 publicado. Ambas densidades sugieren un volumen cercano a 1090 mm³, distinto de 1040; ésta es una observación aritmética, no una corrección demostrada. Hace falta aclaración del fabricante para resolver cuál dato de origen debe cambiar. Según la regla de preferir densidad directa, mantener 642.

## Resumen por núcleo

- Sin salvedad específica, según las convenciones solicitadas: 0T42019EC, 0T44444EC, 0T43939EC, 0T-44949-EC, 0T42625UG, 0T42620UG, 0T42016UG, 0T45050UG, 0T43230UG, 0T44040UG, 0T41506TC, 0T-40603-TC, ZT41605TC, ZT42206TC, ZT43813TC, ZT44015TC, ZT43825TC, ZT47313TC, NT42819UG, NT42316UG, ZT41003TC, 0T40601TC.
- Errores numéricos demostrados en data: ninguno.
- Con reserva de geometría nominal: 0T42523EC (Aw).
- Con inconsistencia del datasheet: NT41812UG (Ploss).
- PDFs ausentes: ninguno. Fuentes no revisadas: ninguna de las 24.

## Código de corrección

No es necesario aplicar un parche. El archivo verificar_data.py permite contrastar tu data con la transcripción independiente y devolver diferencias sin modificarla. Mantiene exactamente los siete campos y comunica las dos reservas.

## Límites de interpretación

Bmax=0.5 mT es la condición de ensayo de AL (10 kHz y 25°C); en EC/UG es <0.5 mT. No es Bsat ni la inducción admisible de diseño. AL es el nominal, no el mínimo y sin aplicar tolerancias. Ploss expresa el límite especificado de ensayo; donde aparece < se conserva la cota numérica, no se transforma en una medición exacta. En los PDFs sin <, el encabezado PL max sigue indicando un límite máximo. Estos datos de 100 kHz no determinan las pérdidas de un PSFB a 400 kHz. Aw no descuenta aislamiento ni factor de llenado. La convención de ventanas por mitad debe revisarse al dimensionar la pareja ensamblada.

## Trazabilidad

El archivo auditoria_168_campos.csv contiene una fila por campo con valor actual, valor contrastado, estado, PDF, página, apartado, fórmula y SHA-256 del PDF. Las fuentes originales se conservan intactas.
