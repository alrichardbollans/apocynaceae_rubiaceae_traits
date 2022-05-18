library(terra)
library(rjson)

configs = rjson::fromJSON(file = '../large_file_storage/my_directories.json')
source(here::here('helper_functions.R'))
import_raster <- function(filename){
  #Linux
  str_name<-paste(configs$raster_download,filename,sep='/')
  # Windows
  #str_name<-paste('C:\\Users\\ari11kg\\Downloads\\rasters',filename,sep='\\')
  print(str_name)
  
  imported_raster=terra::rast(str_name)
  print(imported_raster)
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
  original_raster.aggregate <- terra::aggregate(original_raster,fact=fact, na.rm=TRUE)
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
  print(original_raster)
  aggregated <- terra::aggregate(original_raster,fact=fact,fun=mode_fn)
  print(res(aggregated))
  return (aggregated)
}

project_and_output_rast <- function(original_raster, template_raster, new_name= NULL){
  print('old raster:')
  print(original_raster)
  

  aggregated <- terra::project(original_raster,template_raster)
  
  
  
  if (!is.null(new_name)){
    names(aggregated) = new_name
  }
  write_to_temp_outputs(aggregated)
  print('new raster:')
  print(aggregated)
  return (aggregated)
}

agg_and_output_deg_rast <-function(original_raster, new_name= NULL){
  print('old raster:')
  print(original_raster)
  
  
  aggregated <- agg_deg_raster(original_raster)
  
  if (!is.null(new_name)){
    names(aggregated) = new_name
  }
  write_to_temp_outputs(aggregated)
  print('new raster:')
  print(aggregated)
  return (aggregated)
}

agg_and_output_m_rast <-function(original_raster, new_name= NULL){
  print('old raster:')
  print(original_raster)
  
  
  aggregated <- agg_m_raster(original_raster)
  
  if (!is.null(new_name)){
    names(aggregated) = new_name
  }
  write_to_temp_outputs(aggregated)
  print('new raster:')
  print(aggregated)
  return (aggregated)
}

agg_10kmsoil_and_output <-function(original_raster, new_name= NULL){
  print('old raster:')
  print(original_raster)
  
  
  aggregated <- agg_raster(original_raster,0.2)
  
  if (!is.null(new_name)){
    names(aggregated) = new_name
  }
  write_to_temp_outputs(aggregated)
  print('new raster:')
  print(aggregated)
  return (aggregated)
}


write_to_temp_outputs <- function(r){
  
  summarise_raster(r)
  plot_raster(r)
  
  writeRaster(r,file.path('temp_outputs','prepared rasters',paste(names(r)[1],'.tiff',sep='')),overwrite=TRUE)
  
}

plot_raster <-function(r){
  png(file.path('outputs','raster_plots',paste(names(r)[1],'.png',sep='')), width = 800, height = 600)
  
  plot(r,main=names(r)[1])
  dev.off()
}

average_layers <- function(rasters){
  return(app(rasters, terra::mean))
}

# First get raster in desired format (can then project other rasters to format if needed)
chelsa_bio1 = import_raster('CHELSA_bio1_1981-2010_V.2.1.tif')
chelsa_bio1.aggregated = agg_and_output_deg_rast(chelsa_bio1, 
                                                 new_name = c("mean_air_temp"))

chelsa_bio4 = import_raster('CHELSA_bio4_1981-2010_V.2.1.tif')
chelsa_bio4.aggregated = agg_and_output_deg_rast(chelsa_bio4, 
                                                 new_name = c("temp_seasonality"))

chelsa_bio10 = import_raster('CHELSA_bio10_1981-2010_V.2.1.tif')
chelsa_bio10 = agg_and_output_deg_rast(chelsa_bio10, 
                                       new_name = c("bio10"))

chelsa_bio11 = import_raster('CHELSA_bio11_1981-2010_V.2.1.tif')
chelsa_bio11.aggregated = agg_and_output_deg_rast(chelsa_bio11, 
                                                  new_name = c("bio11"))

chelsa_bio12 = import_raster('CHELSA_bio12_1981-2010_V.2.1.tif')
chelsa_bio12.aggregated = agg_and_output_deg_rast(chelsa_bio12, 
                                                  new_name = c("precip_amount"))

chelsa_bio15 = import_raster('CHELSA_bio15_1981-2010_V.2.1.tif')
chelsa_bio15.aggregated = agg_and_output_deg_rast(chelsa_bio15, 
                                                  new_name = c("precip_seasonality"))

chelsa_bio16 = import_raster('CHELSA_bio16_1981-2010_V.2.1.tif')
chelsa_bio16.aggregated = agg_and_output_deg_rast(chelsa_bio16, 
                                                  new_name = c("bio16"))

chelsa_bio17 = import_raster('CHELSA_bio17_1981-2010_V.2.1.tif')
chelsa_bio17.aggregated = agg_and_output_deg_rast(chelsa_bio17, 
                                                  new_name = c("bio17"))
# Soil
depth_to_bedrock = import_raster('BDTICM_M_10km_ll.tif')
depth_to_bedrock.aggregated = agg_10kmsoil_and_output(depth_to_bedrock,
                                           new_name =  c("soil_depth"))

# Soil rasters are averaged over 30cm depth
wc1 = import_raster('WWP_M_sl1_10km_ll.tif')
wc2 = import_raster('WWP_M_sl2_10km_ll.tif')
wc3 = import_raster('WWP_M_sl3_10km_ll.tif')
wc4 = import_raster('WWP_M_sl4_10km_ll.tif')
water_capacity = average_layers(c(wc1,wc2,wc3,wc4))
water_capacity.aggregated = agg_10kmsoil_and_output(water_capacity,
                                         new_name = c("water_capacity"))


soil_ocs = import_raster('ocs_0-30cm_mean_5000.tif')
soil_ocs.aggregated = agg_and_output_m_rast(soil_ocs,
                                        new_name = c("soil_ocs"))

ph1 = import_raster('phh2o_0-5cm_mean_5000.tif')
ph2 = import_raster('phh2o_5-15cm_mean_5000.tif')
ph3 = import_raster('phh2o_15-30cm_mean_5000.tif')
homo_ph_soil = average_layers(c(ph1,ph2,ph3))
ph_soil.aggregated = agg_and_output_m_rast(homo_ph_soil,
                                       new_name = c("soil_ph"))

nit1 = import_raster('nitrogen_0-5cm_mean_5000.tif')
nit2 = import_raster('nitrogen_5-15cm_mean_5000.tif')
nit3 = import_raster('nitrogen_15-30cm_mean_5000.tif')
homo_nit_soil = average_layers(c(nit1,nit2,nit3))
nit_soil.aggregated = agg_and_output_m_rast(homo_nit_soil,
                                        new_name =  c("soil_nitrogen"))


soc1 = import_raster('soc_0-5cm_mean_5000.tif')
soc2 = import_raster('soc_5-15cm_mean_5000.tif')
soc3 = import_raster('soc_15-30cm_mean_5000.tif')
homo_soc_soil = average_layers(c(soc1,soc2,soc3))
soc_soil.aggregated = agg_and_output_m_rast(homo_soc_soil,
                                        new_name = c("soil_soc"))
# Topography
elevation = import_raster('mn30_grd/mn30_grd')
elevation.aggregated = agg_and_output_deg_rast(elevation,
                                    new_name = c("gmted_elevation"))

slope = terra::terrain(elevation,v="slope")
slope.aggregated = agg_and_output_deg_rast(slope,
                                new_name = c("gmted_slope"))

breakline = import_raster('be30_grd/be30_grd')
breakline.aggregated = agg_and_output_deg_rast(breakline,
                                    new_name = c("gmted_breakline"))


# KG needs specific aggregation
kg = import_raster('Beck_KG_V1_present_0p083.tif')
values(kg)
kg.aggregated = agg_kg_raster(kg)
names(kg.aggregated) <- c("Beck_KG_V1_present")
write_to_temp_outputs(kg.aggregated)
