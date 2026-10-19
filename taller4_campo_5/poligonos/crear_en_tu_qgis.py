from qgis.core import *
from pathlib import Path
from datetime import datetime
datos = [
    ('D1', [(500525, 6811025), (500625, 6811800), (500925, 6812275), (501450, 6812550), (501975, 6813325), (502200, 6813700), (501975, 6814200), (502450, 6814375), (502775, 6814800), (503350, 6814725), (503350, 6814100), (503975, 6814375), (504600, 6814425), (504950, 6815150), (505700, 6815200), (506050, 6814675), (506575, 6814475), (506675, 6814000), (506200, 6813625), (506575, 6813225), (506325, 6812750), (505700, 6812325), (504950, 6811975), (504375, 6811325), (503700, 6810750), (503300, 6810200), (502750, 6810550), (501875, 6810700), (501200, 6810450)]),
    ('D2', [(530175, 6803925), (531075, 6804125), (531825, 6803875), (532375, 6804000), (532825, 6803925), (533175, 6803550), (533550, 6803675), (533925, 6803250), (534425, 6803175), (534800, 6802500), (535250, 6801825), (535750, 6801325), (535750, 6800675), (535750, 6800250), (535175, 6800075), (534325, 6800250), (533500, 6800325), (532925, 6800575), (532500, 6800800), (532000, 6800750), (531425, 6801000), (530825, 6800925), (530325, 6801250), (530000, 6801750), (530125, 6802250), (530425, 6802425), (530050, 6802875)]),
    ('D3', [(529950, 6789725), (530175, 6790425), (530825, 6790925), (531525, 6790850), (531900, 6790425), (532600, 6790600), (533100, 6790150), (533675, 6789725), (533950, 6789075), (534725, 6788750), (535150, 6788200), (535525, 6787550), (535800, 6787025), (536025, 6786475), (535700, 6785925), (536025, 6785400), (535475, 6785000), (534825, 6784950), (534175, 6785275), (533525, 6784950), (532975, 6785275), (532450, 6785075), (531900, 6785500), (531475, 6786050), (530875, 6786250), (530650, 6786950), (530175, 6787350), (530275, 6788150), (529900, 6788750)]),
]
c = QgsVectorLayer('Polygon?crs=EPSG:32719&field=id:string&field=tipo:string', 'Dendriticos propuestos', 'memory')
for nombre, puntos in datos:
    f = QgsFeature(c.fields())
    f.setAttributes([nombre, 'Dendrítico'])
    f.setGeometry(QgsGeometry.fromPolygonXY([[QgsPointXY(x,y) for x,y in puntos + [puntos[0]]]]))
    c.dataProvider().addFeatures([f])
c.updateExtents()
carpeta = QgsProject.instance().homePath() or str(Path.home())
ruta = str(Path(carpeta) / ('dendriticos_propuestos_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.gpkg'))
op = QgsVectorFileWriter.SaveVectorOptions()
op.driverName = 'GPKG'
op.layerName = 'propuestas_nuevas'
resultado = QgsVectorFileWriter.writeAsVectorFormatV3(c, ruta, QgsProject.instance().transformContext(), op)
if resultado[0] != QgsVectorFileWriter.NoError:
    raise RuntimeError(str(resultado))
v = QgsVectorLayer(ruta, 'Dendriticos propuestos - revisar', 'ogr')
v.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'63,210,100,35','outline_color':'0,130,45','outline_width':'0.6'}))
et = QgsPalLayerSettings()
et.fieldName = "id || ' - Dendritico'"
et.isExpression = True
v.setLabeling(QgsVectorLayerSimpleLabeling(et))
v.setLabelsEnabled(True)
v.saveNamedStyle(str(Path(ruta).with_suffix('.qml')))
QgsProject.instance().addMapLayer(v)
print('Creados 3 poligonos nuevos. Archivo guardado en: ' + ruta)
