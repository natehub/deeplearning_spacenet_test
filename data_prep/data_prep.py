# this script is meant to be ran inside OSGeo4W shell's python
import os
import subprocess
from xml.dom.minidom import parse
import xml.dom.minidom
from xml.dom import minidom

def geojson_to_shp():
    '''Convert geojson to shapefile and merge all the shapefiles into a single shapefile'''
    savefile = ""
    for file in os.listdir('buildings'):
        if file.endswith(".geojson"):
            num = os.path.splitext(os.path.basename(file))[0]
            if savefile == "":
                savefile = "merged.shp"
                os.system('ogr2ogr -f "SQLite" -nlt polygon -t_srs EPSG:4326 merged.sqlite "buildings\\{0}.geojson"'.format(num))
            else:
                os.system('ogr2ogr -f "SQLite"  -t_srs EPSG:4326 -update -append merged.sqlite "buildings\\{0}.geojson" -nln merged'.format(num))

    print("final file merged: " + savefile)


def retile_images(smalltiles, rasterinput, width, height):
    '''tile images into a smaller size'''
    for fileSR in os.listdir(rasterinput):
        if fileSR.endswith(".tif"):
            smallrast = os.path.splitext(os.path.basename(fileSR))[0]
            # print(rasterinput+raster)
            os.system('gdal_retile -s_srs EPSG:4326 -r bilinear  -ps {0} {1} -targetDir {2}  {3}{4}.tif'.format(str(width),str(height), smalltiles,rasterinput,smallrast))
    print("we finished re-tiling images!")


def build_stats(rasterinput):
    '''build statistics on rasters'''
    for fileTIF in os.listdir(rasterinput):
        if fileTIF.endswith(".tif"):
            vrt = os.path.splitext(os.path.basename(fileTIF))[0]
            os.system('gdalinfo "{0}{1}.tif" -stats'.format(rasterinput, vrt))
    print("we finished building statistics!")


def raster_to_VRT(rasterinput,rasteroutput):
    '''Convert rasters into VRT'''
    for fileR in os.listdir(rasterinput):
        if fileR.endswith(".tif"):
            raster = os.path.splitext(os.path.basename(fileR))[0]
            # print(rasterinput+raster)
            os.system(
                'gdal_translate -a_nodata 0 -of VRT {0}{1}.tif {2}{3}.vrt'.format(rasterinput, raster, rasteroutput, raster))
    print("we finished converting raster to VRT!")


def hist_min_max(vrttiles):
    dict = {'1max': 0.1, "1min": 1000.1, '2max': 0.1, "2min": 1000.1, '3max': 0.1, "3min": 1000.1}

    arraydict = []
    for fileTRAN in os.listdir(vrt_tiles):
        #print(vrt_tiles+fileTRAN)
        if fileTRAN.endswith(".vrt"):
            xmled = os.path.splitext(os.path.basename(fileTRAN))[0]
            doc = minidom.parse(vrt_tiles+fileTRAN)
            bands = doc.getElementsByTagName("VRTRasterBand")
            for band in bands:
                sid = band.getAttribute("band")
                #print(sid)
                if sid == "1":

                    maximum = band.getElementsByTagName("MDI")[0]
                    minimum = band.getElementsByTagName("MDI")[2]
                    #print(maximum.firstChild.data)
                    #print(minimum.firstChild.data)
                    maximum = maximum.firstChild.data
                    minimum = minimum.firstChild.data
                    if float(maximum)>float(dict['1max']) and float(maximum) > 0:
                        dict['1max'] = float(maximum)
                        print("max")
                        print(dict['1max'])
                    if float(minimum)<float(dict['1min']) and  float(minimum) > 0:
                        dict['1min'] = float(minimum)
                        print("min")
                        print(dict['1min'])
                elif sid == "2":
                    maximum = band.getElementsByTagName("MDI")[0]
                    minimum = band.getElementsByTagName("MDI")[2]
                    # print(maximum.firstChild.data)
                    # print(minimum.firstChild.data)
                    maximum = maximum.firstChild.data
                    minimum = minimum.firstChild.data
                    if float(maximum)>float(dict['2max']) and float(maximum) > 0:
                        dict['2max'] = float(maximum)
                        print("max")
                        print(dict['2max'])
                    if float(minimum)<float(dict['2min']) and  float(minimum) > 0:
                        dict['2min'] = float(minimum)
                        print("min")
                        print(dict['2min'])
                elif sid == "3":
                    maximum = band.getElementsByTagName("MDI")[0]
                    minimum = band.getElementsByTagName("MDI")[2]
                    # print(maximum.firstChild.data)
                    # print(minimum.firstChild.data)
                    maximum = maximum.firstChild.data
                    minimum = minimum.firstChild.data
                    if float(maximum)>float(dict['3max']) and float(maximum) > 0:
                        dict['3max'] = float(maximum)
                        print("max")
                        print(dict['3max'])
                    if float(minimum)<float(dict['3min']) and  float(minimum) > 0:
                        dict['3min'] = float(minimum)
                        print("min")
                        print(dict['3min'])
    print(dict)


def create_jpgs_one(small_tiles, vrt_tiles,jpgoutput):
    # reconstruct min max based off of each tifs attributes min max values
    dict = {'1max': 0, "1min": 0, '2max': 0, "2min": 0, '3max': 0, "3min": 0}
    arraydict = []

    for fileTRAN in os.listdir(vrt_tiles):
        if fileTRAN.endswith(".vrt"):
            xmled = os.path.splitext(os.path.basename(fileTRAN))[0]

            DOMTREE = xml.dom.minidom.parse("{0}{1}.tif.aux.xml".format(small_tiles, xmled))
            collection = DOMTREE.documentElement
            bands = collection.getElementsByTagName('Metadata')
            cont = 0
            for ba in bands:
                hist1 = ba.getElementsByTagName('MDI')[2]
                hist2 = ba.getElementsByTagName('MDI')[0]
                mind = hist1.childNodes[0].data
                maxd = hist2.childNodes[0].data
                # print(mind)
                # print(maxd)
                cont = cont + 1
                dict[str(cont) + 'max'] = maxd
                dict[str(cont) + 'min'] = mind

            print(dict['1max'])
            print(dict['2max'])
            print(dict['3max'])
            arraydict.append(dict)
            if str(dict['1max']) == "0" and str(dict['2max']) == "0" and str(dict['3max']) =="0" :
                pass
            else:
                os.system(
                    'gdal_translate -scale_1 {0} {1} -scale_2 {2} {3} -scale_3 {4} {5}  -ot Byte -of JPEG {6}{7}.vrt {8}{9}.jpg'.format(
                        dict['1min'], dict['1max'], dict['2min'], dict['2max'], dict['3min'], dict['3max'], vrt_tiles,
                        xmled, jpgoutput, xmled))
    print("we finished!")




def create_jpgs_all(small_tiles, vrt_tiles,jpgoutput):
    # reconstruct min max based off of each tifs attributes
    dict = {'1max': 0, "1min": 0, '2max': 0, "2min": 0, '3max': 0, "3min": 0}
    arraydict = []

    for fileTRAN in os.listdir(vrt_tiles):
        if fileTRAN.endswith(".vrt"):
            xmled = os.path.splitext(os.path.basename(fileTRAN))[0]

            DOMTREE = xml.dom.minidom.parse("{0}{1}.tif.aux.xml".format(small_tiles, xmled))
            collection = DOMTREE.documentElement
            bands = collection.getElementsByTagName('Metadata')
            cont = 0
            for ba in bands:
                hist1 = ba.getElementsByTagName('MDI')[2]
                hist2 = ba.getElementsByTagName('MDI')[0]
                mind = hist1.childNodes[0].data
                maxd = hist2.childNodes[0].data
                # print(mind)
                # print(maxd)
                cont = cont + 1
                dict[str(cont) + 'max'] = maxd
                dict[str(cont) + 'min'] = mind

            print(dict['1max'])
            print(dict['2max'])
            print(dict['3max'])
            arraydict.append(dict)
            if str(dict['1max']) == "0" and str(dict['2max']) == "0" and str(dict['3max']) =="0" :
                pass
            else:
                os.system(
                    'gdal_translate -scale_1 1.0 1933.0 -scale_2 77.0 1841.0 -scale_3 49.0 1577.0 -exponent .7  -ot Byte -of JPEG {6}{7}.vrt {8}{9}.jpg'.format(
                        dict['1min'], dict['1max'], dict['2min'], dict['2max'], dict['3min'], dict['3max'], vrt_tiles,
                        xmled, jpgoutput, xmled))
    print("we finished!")


image_width = 130
image_height = 130

new_tiles = "C:\\code\\deeplearning\\_data\\paris\\"
original_rasters = "F:\\digitalglobe_imagery\\AOI_3_Paris_Train\\RGB-PanSharpen\\"
vrt_tiles = "C:\\code\\deeplearning\\_data\\vrt_paris\\"
jpg_images = "C:\\code\\deeplearning\\_data\\jpg_paris\\"

tilraw = "F:\\geoss\\RGB-PanSharpen\\"
tilevrt = "F:\\geoss\\vrt\\"

#geojson_to_shp()

#retile_images(new_tiles, original_rasters, image_width, image_height)

#raster_to_VRT(new_tiles,vrt_tiles)
#raster_to_VRT(tilraw,tilevrt)
#build_stats(new_tiles)
#hist_min_max(vrt_tiles)
#need to add min max to each band from hist_min_max() function to the below function
#create_jpgs_all(new_tiles, vrt_tiles,jpg_images)


#os.system('gdaltindex index2.shp "{0}*.jpg"'.format(jpg_images))