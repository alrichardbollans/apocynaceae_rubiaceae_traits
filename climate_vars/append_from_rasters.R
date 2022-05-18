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
species_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/cleaned_sp_occurences.csv',sep='/'))
subspecies_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/cleaned_subsp_occurences.csv',sep='/'))
varis_df = read.csv(paste(configs$large_folders,'plant_occurence_vars/outputs/cleaned_vari_occurences.csv',sep='/'))

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

# Need to restart R each time to clean memory
r1 = prepared_rasters[[1]]
occ_df<-append_var_to_df(occ_df,r1)
.rs.restartR()

prepared_rasters = read_rasters()
r2 = prepared_rasters[[2]]
occ_df<-append_var_to_df(occ_df,r2)
.rs.restartR()

prepared_rasters = read_rasters()
r3 = prepared_rasters[[3]]
occ_df<-append_var_to_df(occ_df,r3)
.rs.restartR()

prepared_rasters = read_rasters()
r4 = prepared_rasters[[4]]
occ_df<-append_var_to_df(occ_df,r4)
.rs.restartR()

prepared_rasters = read_rasters()
r5 = prepared_rasters[[5]]
occ_df<-append_var_to_df(occ_df,r5)
.rs.restartR()

prepared_rasters = read_rasters()
r6 = prepared_rasters[[6]]
occ_df<-append_var_to_df(occ_df,r6)
.rs.restartR()

prepared_rasters = read_rasters()
r7 = prepared_rasters[[7]]
occ_df<-append_var_to_df(occ_df,r7)
.rs.restartR()

prepared_rasters = read_rasters()
r8 = prepared_rasters[[8]]
occ_df<-append_var_to_df(occ_df,r8)
.rs.restartR()

prepared_rasters = read_rasters()
r9 = prepared_rasters[[9]]
occ_df<-append_var_to_df(occ_df,r9)
.rs.restartR()

prepared_rasters = read_rasters()
r10 = prepared_rasters[[10]]
occ_df<-append_var_to_df(occ_df,r10)
.rs.restartR()

prepared_rasters = read_rasters()
r11 = prepared_rasters[[11]]
occ_df<-append_var_to_df(occ_df,r11)
write.csv(occ_df, paste(configs$large_folders,'occ_climate_vars/occ_with_climate_vars.csv',sep='/'))
.rs.restartR()


prepared_rasters = read_rasters()
r12 = prepared_rasters[[12]]
occ_df<-append_var_to_df(occ_df,r12)
.rs.restartR()

prepared_rasters = read_rasters()
r13 = prepared_rasters[[13]]
occ_df<-append_var_to_df(occ_df,r13)
.rs.restartR()

prepared_rasters = read_rasters()
r14 = prepared_rasters[[14]]
occ_df<-append_var_to_df(occ_df,r14)
.rs.restartR()

prepared_rasters = read_rasters()
r15 = prepared_rasters[[15]]
occ_df<-append_var_to_df(occ_df,r15)
.rs.restartR()

prepared_rasters = read_rasters()
r16 = prepared_rasters[[16]]
occ_df<-append_var_to_df(occ_df,r16)
write.csv(occ_df, paste(configs$large_folders,'occ_climate_vars/occ_with_climate_vars.csv',sep='/'))
.rs.restartR()

prepared_rasters = read_rasters()
r17 = prepared_rasters[[17]]
occ_df<-append_var_to_df(occ_df,r17)
.rs.restartR()

prepared_rasters = read_rasters()
r18 = prepared_rasters[[18]]
occ_df<-append_var_to_df(occ_df,r18)
write.csv(occ_df, paste(configs$large_folders,'occ_climate_vars/occ_with_climate_vars.csv',sep='/'))


