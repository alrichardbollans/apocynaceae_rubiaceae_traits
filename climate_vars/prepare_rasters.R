library(terra)
library(rjson)

configs = rjson::fromJSON(file = '../large_file_storage/my_directories.json')

import_raster <- function(filename){
  str_name<-paste(configs$raster_download,filename,sep='/')
  print(str_name)
  imported_raster=rast(str_name)
  return(imported_raster)
}

# 0.16666 corresponds to 20km resolution
desired_deg_resolution = 0.16666666666666666666667
desired_m_resolution = 20000
desired_proj <- "+proj=longlat +datum=WGS84 +no_defs"

# sg is 250m resolution
#chelsa and kg are 1000m resolution
agg_raster <- function(original_raster,desired_resolution){
  fact = desired_resolution/res(original_raster)
  print(res(original_raster))
  print(fact)
  original_raster.aggregate <- aggregate(original_raster,fact=fact)
  print(res(original_raster.aggregate))
  return (original_raster.aggregate)
}
agg_deg_raster <- function(original_raster){
  agg_raster(original_raster,desired_deg_resolution)
}

agg_m_raster<-function(original_raster){
  agg_raster(original_raster,desired_m_resolution)
}

agg_kg_raster <- function(original_raster){
  print(res(original_raster))
  fact = desired_deg_resolution/res(original_raster)
  print(fact)
  aggregated <- aggregate(original_raster,fact=fact,fun=modal,na.rm=TRUE, ties='random')
  print(res(aggregated))
  return (aggregated)
}
project_rast <- function(original_raster, template_raster, new_name= NULL){
  print(res(original_raster))
  aggregated <- project(original_raster,template_raster)
  print(res(aggregated))
  
  if (!is.null(new_name)){
    names(aggregated) = new_name
  }
  write_to_temp_outputs(aggregated)
  return (aggregated)
}

summarise_raster <- function(r){
  print(names(r))
  print(minmax(r))
  print(res(r))
}
write_to_temp_outputs <- function(r){
  
  summarise_raster(r)
  writeRaster(r,file.path('temp_outputs/prepared rasters',paste(names(r)[1],'.tiff',sep='')),overwrite=TRUE)
  
}



# First get raster in desired format
chelsa_bio1 = import_raster('CHELSA_bio1_1981-2010_V.2.1.tif')
chelsa_bio1.aggregated = agg_deg_raster(chelsa_bio1)
write_to_temp_outputs(chelsa_bio1.aggregated)

# Then project other rasters to format
elevation = import_raster('mn30_grd/mn30_grd')
elevation.aggregated = project_rast(elevation,chelsa_bio1.aggregated,new_name = c("gmted_elevation"))

slope = terra::terrain(elevation,v="slope")
slope.aggregated = project_rast(slope,chelsa_bio1.aggregated, new_name = c("gmted_slope"))


chelsa_bio4 = import_raster('CHELSA_bio4_1981-2010_V.2.1.tif')
chelsa_bio4.aggregated = project_rast(chelsa_bio4,chelsa_bio1.aggregated)

chelsa_bio10 = import_raster('CHELSA_bio10_1981-2010_V.2.1.tif')
chelsa_bio10 = project_rast(chelsa_bio10,chelsa_bio1.aggregated)

chelsa_bio11 = import_raster('CHELSA_bio11_1981-2010_V.2.1.tif')
chelsa_bio11.aggregated = project_rast(chelsa_bio11,chelsa_bio1.aggregated)

chelsa_bio12 = import_raster('CHELSA_bio12_1981-2010_V.2.1.tif')
chelsa_bio12.aggregated = project_rast(chelsa_bio12,chelsa_bio1.aggregated)

chelsa_bio15 = import_raster('CHELSA_bio15_1981-2010_V.2.1.tif')
chelsa_bio15.aggregated = project_rast(chelsa_bio15,chelsa_bio1.aggregated)

chelsa_bio16 = import_raster('CHELSA_bio16_1981-2010_V.2.1.tif')
chelsa_bio16.aggregated = project_rast(chelsa_bio16,chelsa_bio1.aggregated)

chelsa_bio17 = import_raster('CHELSA_bio17_1981-2010_V.2.1.tif')
chelsa_bio17.aggregated = project_rast(chelsa_bio17,chelsa_bio1.aggregated)

depth_to_bedrock = import_raster('BDTICM_M_10km_ll.tif')
depth_to_bedrock.aggregated = project_rast(depth_to_bedrock,chelsa_bio1.aggregated, new_name =  c("soil_depth"))

water_capacity = import_raster('WWP_M_sl1_10km_ll.tif')
water_capacity.aggregated = project_rast(water_capacity,chelsa_bio1.aggregated, new_name = c("water_capacity"))


soil_ocs = import_raster('ocs_0-30cm_mean_5000_homolosine.tif')
soil_ocs.aggregated = project_rast(soil_ocs,chelsa_bio1.aggregated, new_name = c("soil_ocs_0-30cm_mean"))

homo_ph_soil = import_raster('phh2o_0-5cm_mean_homolosine.tif')
ph_soil.aggregated = project_rast(homo_ph_soil,chelsa_bio1.aggregated,new_name = c("phh2o_0-5cm_mean"))


homo_nit_soil = import_raster('nitrogen_0-5cm_mean_homolosine.tif')
nit_soil.aggregated = project_rast(homo_nit_soil,chelsa_bio1.aggregated, new_name =  c("nitrogen_0-5cm_mean"))

homo_soc_soil = import_raster('soc_0-5cm_mean_homolosine.tif')
soc_soil.aggregated = project_rast(homo_soc_soil,chelsa_bio1.aggregated, new_name = c("soc_0-5cm_mean"))


breakline = import_raster('gmted10_breaklineemph.tif')
breakline.aggregated = project_rast(breakline,chelsa_bio1.aggregated, new_name = c("gmted_breakline"))

# KG needs specific aggregation
kg = import_raster('Beck_KG_V1_present_0p083.tif')
values(kg)
kg.aggregated = agg_kg_raster(kg)
names(kg.aggregated) <- c("Beck_KG_V1_present")
write_to_temp_outputs(kg.aggregated)
