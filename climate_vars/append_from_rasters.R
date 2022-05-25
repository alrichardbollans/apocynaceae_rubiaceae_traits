library(terra)
library(rjson)
library(dplyr)

configs = rjson::fromJSON(file = '../large_file_storage/my_directories.json')
source(here::here('helper_functions.R'))
read_rasters <- function(){
  prep_rasters=list()
  raster_files = list.files(path=file.path('temp_outputs','prepared rasters'), pattern='*.tiff$')
  for (r in raster_files){
    
    prepped_raster = rast(file.path('temp_outputs','prepared rasters',r))
    summarise_raster(prepped_raster)
    prep_rasters[[length(prep_rasters)+1]]<-prepped_raster
  }
  
  return(prep_rasters)
}

prepared_rasters = read_rasters()

# Get dataframe containing cleaned occurences
native = TRUE # Whether to look at occurrences from native or introduced regions
if (native){
  species_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/native/cleaned_sp_occurences.csv',sep='/'))
  subspecies_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/native/cleaned_subsp_occurences.csv',sep='/'))
  varis_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/native/cleaned_vari_occurences.csv',sep='/'))
} else{
  species_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/introduced/cleaned_sp_occurences.csv',sep='/'))
  subspecies_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/introduced/cleaned_subsp_occurences.csv',sep='/'))
  varis_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/introduced/cleaned_vari_occurences.csv',sep='/'))
}

occ_df_with_duplicates = rbind(species_df,subspecies_df)
occ_df_with_duplicates = rbind(occ_df_with_duplicates,varis_df)

occ_df = dplyr::distinct(occ_df_with_duplicates, gbifID, .keep_all = TRUE)

# Save some RAM
rm(occ_df_with_duplicates)
rm(species_df)
rm(subspecies_df)
rm(varis_df)
gc()
append_var_to_df <- function(df,reaggragated_raster){
  
  # Update names
  names(reaggragated_raster) = varnames(reaggragated_raster)
  print(names(reaggragated_raster))
  lat_long_vect <- terra::vect(df,geom= c("decimalLongitude", "decimalLatitude"), crs="+proj=longlat")
  reprojected_vect <- terra::project(lat_long_vect, crs(reaggragated_raster))
  
  var_values = data.frame(extract(reaggragated_raster, reprojected_vect))

  bound_df = cbind(df, var_values)
  bound_df <- bound_df %>% select(-ID)
  return(bound_df)
}

for (r in prepared_rasters){
  occ_df<-append_var_to_df(occ_df,r)
  gc()
}


names(occ_df)[names(occ_df)=="decimalLatitude"] <- "latitude"
names(occ_df)[names(occ_df)=="decimalLongitude"] <- "longitude"


if (native){
  write.csv(occ_df, paste(configs$large_folders,'occ_climate_vars/native/occ_with_climate_vars.csv',sep='/'))
} else{
  write.csv(occ_df, paste(configs$large_folders,'occ_climate_vars/introduced/occ_with_climate_vars.csv',sep='/'))
}



