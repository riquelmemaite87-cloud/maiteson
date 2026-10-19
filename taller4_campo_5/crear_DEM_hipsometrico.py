# Taller 4 - Mapa 1: DEM clasificado por elevacion
# Ejecutar dentro de QGIS con el DEM recortado seleccionado en el panel Capas.
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsRasterBandStats,
    QgsSingleBandPseudoColorRenderer, QgsRasterShader, QgsColorRampShader,
    QgsPrintLayout, QgsLayoutItemPage, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemLegend, QgsLayoutItemScaleBar, QgsLayoutPoint, QgsLayoutSize,
    QgsLayoutExporter, QgsUnitTypes
)
from qgis.PyQt.QtCore import QStandardPaths
from qgis.PyQt.QtGui import QColor, QFont
from pathlib import Path

# Reemplaza solo este texto por tu nombre y apellido.
ESTUDIANTE = 'NOMBRE APELLIDO'
CAMPO = 'Campo 5'
N_CLASES = 8                         # El taller exige entre 5 y 15.

project = QgsProject.instance()
layer = iface.activeLayer()
if not isinstance(layer, QgsRasterLayer):
    raise Exception('Selecciona primero el raster DEM recortado en el panel Capas.')

# Evita usar por accidente hillshade, pendientes o el raster binario.
nombre = layer.name().lower()
if any(x in nombre for x in ('hillshade', 'pendiente', 'sombra')):
    raise Exception('La capa seleccionada no parece ser el DEM. Selecciona dem_campo_5 o el DEM recortado equivalente.')

if layer.bandCount() < 1:
    raise Exception('El raster seleccionado no tiene una banda utilizable.')

# Estadisticas reales del DEM; no se inventan rangos.
stats = layer.dataProvider().bandStatistics(1, QgsRasterBandStats.All, layer.extent(), 0)
minv = float(stats.minimumValue)
maxv = float(stats.maximumValue)
if minv >= maxv:
    raise Exception('No se pudieron obtener min/max del DEM.')

# Clasificacion discreta con colores ordenados de menor a mayor elevacion.
colors = [
    '#2166ac', '#67a9cf', '#d1e5f0', '#f7f7f7',
    '#fddbc7', '#ef8a62', '#b2182b', '#67001f'
]
shader = QgsRasterShader()
color_shader = QgsColorRampShader()
color_shader.setColorRampType(QgsColorRampShader.Discrete)
items = []
for i in range(N_CLASES):
    limite = minv + (maxv - minv) * (i + 1) / N_CLASES
    if i == N_CLASES - 1:
        limite = maxv
    etiqueta = f'{minv + (maxv-minv)*i/N_CLASES:.0f}–{limite:.0f} m s.n.m.'
    items.append(QgsColorRampShader.ColorRampItem(limite, QColor(colors[i]), etiqueta))
color_shader.setColorRampItemList(items)
shader.setRasterShaderFunction(color_shader)
layer.setRenderer(QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader))
layer.triggerRepaint()

# Utilidades de composicion.
def etiqueta(layout, texto, x, y, w, h, tam=9, color='#222222'):
    item = QgsLayoutItemLabel(layout)
    item.setText(texto)
    item.setFont(QFont('DejaVu Sans', tam))
    item.setFontColor(QColor(color))
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x, y))
    item.attemptResize(QgsLayoutSize(w, h))
    return item

layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.pageCollection().pages()[0].setPageSize('A4', QgsLayoutItemPage.Portrait)

añadir = etiqueta
anadir(layout, f'DEM hipsométrico — {CAMPO}', 12, 8, 180, 10, 16)
anadir(layout, f'Clasificación discreta de elevación | {ESTUDIANTE}', 12, 18, 180, 7, 9, '#555555')
anadir(layout, 'Sistema de coordenadas: WGS 84 / UTM zona 19S (EPSG:32719)', 12, 25, 180, 7, 8, '#555555')

mapa = QgsLayoutItemMap(layout)
layout.addLayoutItem(mapa)
mapa.attemptMove(QgsLayoutPoint(18, 34))
mapa.attemptResize(QgsLayoutSize(174, 206))
ext = layer.extent()
ext.scale(1.02)
mapa.setExtent(ext)
mapa.setLayers([layer])
mapa.setBackgroundColor(QColor('white'))

leyenda = QgsLayoutItemLegend(layout)
layout.addLayoutItem(leyenda)
leyenda.setTitle('Elevación (m s.n.m.)')
leyenda.setLinkedMap(mapa)
leyenda.setAutoUpdateModel(False)
raiz = leyenda.model().rootGroup()
raiz.removeAllChildren()
raiz.addLayer(layer)
leyenda.attemptMove(QgsLayoutPoint(18, 244))
leyenda.attemptResize(QgsLayoutSize(174, 35))

barra = QgsLayoutItemScaleBar(layout)
barra.setStyle('Single Box')
barra.setLinkedMap(mapa)
barra.setUnits(QgsUnitTypes.DistanceKilometers)
barra.setUnitLabel('km')
barra.setUnitsPerSegment(5)
barra.setNumberOfSegments(2)
barra.setNumberOfSegmentsLeft(0)
barra.setFont(QFont('DejaVu Sans', 8))
layout.addLayoutItem(barra)
barra.attemptMove(QgsLayoutPoint(18, 283))

# La pauta permite flecha norte o indicacion de orientacion.
anadir(layout, 'N ↑', 178, 282, 18, 12, 13)
anadir(layout, f'Rango del DEM: {minv:.0f}–{maxv:.0f} m s.n.m. | {N_CLASES} clases de igual intervalo', 45, 283, 125, 12, 8, '#555555')

# Guardar en el Escritorio del sistema.
escritorio = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
if not escritorio:
    escritorio = project.homePath() or str(Path.home())
out = Path(escritorio) / 'DEM_hipsometrico.pdf'
resultado = QgsLayoutExporter(layout).exportToPdf(str(out), QgsLayoutExporter.PdfExportSettings())
if resultado != QgsLayoutExporter.Success:
    raise Exception('QGIS no pudo exportar el PDF.')
print(f'Listo: {out}')
print(f'Rango usado: {minv:.2f}–{maxv:.2f} m s.n.m.; clases: {N_CLASES}')
