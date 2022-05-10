library(terra)
library(rjson)
library(dplyr)

configs = rjson::fromJSON(file = '../large_file_storage/my_directories.json')

read_rasters <- function(){
  prep_rasters=list()
  raster_files = list.files(path='temp_outputs/prepared rasters', pattern='*.tiff$')
  for (r in raster_files){
    print(r)
    prepped_raster = rast(file.path('temp_outputs/prepared rasters',r))
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

append_var_to_df <- function(df,reaggragated_raster){
  var_values = data.frame(extract(reaggragated_raster, df[, c("decimalLongitude", "decimalLatitude")], factors=FALSE))
  bound_df = cbind(df, var_values)
  
  return(bound_df)
}


for (r in prepared_rasters){
  print(names(r))
  occ_df<-append_var_to_df(occ_df,r)
}
occ_df <- occ_df %>% select(-ID)
names(occ_df)[names(occ_df)=="COUNT"] <- "gmted_elevation"
write.csv(occ_df, paste(configs$large_folders,'occ_climate_vars/occ_with_climate_vars.csv',sep='/'))
