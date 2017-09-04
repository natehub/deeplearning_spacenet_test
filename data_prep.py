# this script is meant to be run inside OSGeo4W shell's python

import os
#convert geojson to shapefile and from shapefile merge all the shapefiles into a single shapefile
savefile=""
for file in os.listdir('buildings'):
    if file.endswith(".geojson"):
        num = os.path.splitext(os.path.basename(file))[0]
        os.system('ogr2ogr -f "GeoJSON" -t_srs EPSG:4326 "buildings_new\\{0}.shp" "buildings\\{1}.geojson" '.format(num, num))
        if savefile == "":
            savefile = "merged.shp"
            os.system('ogr2ogr -f "esri shapefile merged.shp "buildings_new\\{0}.shp"'.format(num))
        else:
            os.system('ogr2ogr -f "ESRI Shapefile" -update -append merged.shp "buildings_new\\{0}.shp" -nln Merged'.format(num))

print("final file merged: "+ savefile)
os.system('ogr2ogr -f "esri shapefile" -t_srs EPSG:4326 merged.geojson merged.shp ')


# cycle through the imagery and export out a bounding box
imagedirect =  "F:\\digitalglobe_imagery\\AOI_3_Paris_Train\\RGB-PanSharpen\\"
os.system('gdaltindex index.shp "{0}*.tif"'.format(imagedirect))

