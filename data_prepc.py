

import os
import subprocess
from xml.dom.minidom import parse
import xml.dom.minidom

rasterinput='F:\\digitalglobe_imagery\\AOI_3_Paris_Train\\RGB-PanSharpen\\'
rasteroutput = 'F:\\digitalglobe_imagery\\outdata\\'



smalltiles = 'F:\\digitalglobe_imagery\\small_tiles\\'

for fileSR in os.listdir(rasterinput):
    if fileSR.endswith(".tif"):
        smallrast = os.path.splitext(os.path.basename(fileSR))[0]
        #print(rasterinput+raster)
        os.system('gdal_retile -s_srs EPSG:4326 -ps 325 325 -targetDir {0}  {1}{2}.tif'.format(smalltiles,rasterinput,smallrast))

rasterinput = smalltiles

# convert tif's to jpeg's

for fileR in os.listdir(rasterinput):
    if fileR.endswith(".tif"):
        raster = os.path.splitext(os.path.basename(fileR))[0]
        #print(rasterinput+raster)
        os.system('gdal_translate -a_nodata 0 -of VRT {0}{1}.tif {2}{3}.vrt'.format(rasterinput,raster,rasteroutput,raster))

#build statistic on the tif files to compute the min and max for each band
for fileTIF in os.listdir(rasterinput):
    if fileTIF.endswith(".tif"):
        vrt = os.path.splitext(os.path.basename(fileTIF))[0]
        os.system('gdalinfo "{0}{1}.tif" -stats'.format(rasterinput, vrt))


#reconstruct min max based off of each tifs attributes
dict = {'1max':0, "1min":0, '2max':0, "2min":0,'3max':0, "3min":0}
arraydict = []
jpgoutput = 'F:\\digitalglobe_imagery\\jpgout\\'

for fileTRAN in os.listdir(rasteroutput):
    if fileTRAN.endswith(".vrt"):
        xmled = os.path.splitext(os.path.basename(fileTRAN))[0]

        DOMTREE = xml.dom.minidom.parse("{0}{1}.tif.aux.xml".format(rasterinput,xmled))
        collection = DOMTREE.documentElement
        bands = collection.getElementsByTagName('HistItem')
        cont = 0
        for ba in bands:
            hist1 = ba.getElementsByTagName('HistMin')[0]
            hist2 = ba.getElementsByTagName('HistMax')[0]
            mind = hist1.childNodes[0].data
            maxd =hist2.childNodes[0].data
            #print(mind)
            #print(maxd)
            cont = cont +1
            dict[str(cont)+'max'] = maxd
            dict[str(cont)+'min'] = mind

        print(dict['1max'])
        print(dict['2max'])
        print(dict['3max'])
        arraydict.append(dict)
        os.system('gdal_translate -scale_1 {0} {1} -scale_2 {2} {3} -scale_3 {4} {5}  -ot Byte -of JPEG {6}{7}.vrt {8}{9}.jpg'.format(dict['1min'], dict['1max'], dict['2min'],dict['2max'], dict['3min'], dict['3max'],rasteroutput,xmled,jpgoutput,xmled))


#create min and max off of average of all the tifs attributes
b_1min = float(arraydict[0]['1min'])
b_1max = float(arraydict[0]['1max'])

b_2min = float(arraydict[0]['2min'])
b_2max = float(arraydict[0]['2max'])

b_3min = float(arraydict[0]['3min'])
b_3max = float(arraydict[0]['3max'])


for stats in arraydict:
    if  float(stats['1min'])< b_1min:
        b_1min = float(stats['1min'])

    if  float(stats['1max'])>b_1max:
        b_1max = float(stats['1max'])


    if float(stats['2min']) < b_2min:
        b_2min = float(stats['2min'])

    if  float(stats['2max'])> b_2max:
        b_2max = float(stats['2max'])

    if  float(stats['3min']) < b_3min:
        b_3min = float(stats['3min'])

    if  float(stats['3max']) > b_3max:
        b_3max = float(stats['3max'])

arraylength = len(stats)

jpgoutputALL = 'F:\\digitalglobe_imagery\\jpgoutALL\\'

for fileALL in os.listdir(rasteroutput):
    if fileALL.endswith(".vrt"):
        ALLrast = os.path.splitext(os.path.basename(fileALL))[0]
        os.system('gdal_translate -scale_1 {0} {1} -scale_2 {2} {3} -scale_3 {4} {5}  -ot Byte -of JPEG {6}{7}.vrt {8}{9}.jpg'.format(b_1min, b_1max, b_2min, b_2max, b_3min, b_3max, rasteroutput, ALLrast, jpgoutputALL, ALLrast))
