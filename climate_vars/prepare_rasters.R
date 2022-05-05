library(terra)

import_raster <- function(filename){
  str_name<-paste("/home/atp/Downloads/rasters/",filename,sep='')
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
  aggregated <- aggregate(original_raster,fact=fact,fun=modal,na.rm=TRUE)
  print(res(aggregated))
  return (aggregated)
}

project_rast <- function(original_raster, template_raster){
  print(res(original_raster))
  aggregated <- project(original_raster,template_raster)
  print(res(aggregated))
  return (aggregated)
}

# KG needs specific aggregation
kg = import_raster('Beck_KG_V1_present_0p0083.tif')
kg.aggregated = agg_kg_raster(kg)

# First get raster in desired format
chelsa_bio1 = import_raster('CHELSA_bio1_1981-2010_V.2.1.tif')
chelsa_bio1.aggregated = agg_deg_raster(chelsa_bio1)

# Then project other rasters to format

chelsa_bio12 = import_raster('CHELSA_bio12_1981-2010_V.2.1.tif')
chelsa_bio12.aggregated = project_rast(chelsa_bio12,chelsa_bio1.aggregated)

homo_ph_soil = import_raster('phh2o_0-5cm_mean_homolosine.tif')
ph_soil.aggregated = project_rast(homo_ph_soil,chelsa_bio1.aggregated)

homo_nit_soil = import_raster('nitrogen_0-5cm_mean_homolosine.tif')
nit_soil.aggregated = project_rast(homo_nit_soil,chelsa_bio1.aggregated)

homo_soc_soil = import_raster('soc_0-5cm_mean_homolosine.tif')
soc_soil.aggregated = project_rast(homo_soc_soil,chelsa_bio1.aggregated)

breakline = import_raster('gmted10_breaklineemph.tif')
breakline.aggregated = project_rast(breakline,chelsa_bio1.aggregated)
names(breakline.aggregated) <- c("gmted_breakline")

prepared_rasters = list(chelsa_bio1.aggregated,chelsa_bio12.aggregated,
                     ph_soil.aggregated,nit_soil.aggregated,
                     soc_soil.aggregated,kg.aggregated,breakline.aggregated)


#writeRaster(breakline.aggregated,file.path('temp_outputs/prepared rasters',paste(names(breakline.aggregated)[1],'.tiff',sep='')),overwrite=TRUE)

for (r in prepared_rasters){
  print(names(r))
  print(res(r))
  writeRaster(r,file.path('temp_outputs/prepared rasters',paste(names(r)[1],'.tiff',sep='')),overwrite=TRUE)
}
