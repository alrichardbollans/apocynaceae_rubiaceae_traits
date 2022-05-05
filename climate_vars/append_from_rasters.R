library(terra)


read_rasters <- function(){
  prep_rasters=list()
  raster_files = list.files(path='temp_outputs/prepared rasters', pattern='*.tiff')
  for (r in raster_files){
    prepped_raster = rast(file.path('temp_outputs/prepared rasters',r))
    prep_rasters[[length(prep_rasters)+1]]<-prepped_raster
  }
  return(prep_rasters)
}

prepared_rasters = read_rasters()

# Get dataframe containing cleaned occurences
species_df = read.csv('/home/atp/Documents/work life/Kew/large folders/plant_occurence_vars/outputs/cleaned_sp_occurences.csv')
subspecies_df = read.csv('/home/atp/Documents/work life/Kew/large folders/plant_occurence_vars/outputs/cleaned_subsp_occurences.csv')
varis_df = read.csv('/home/atp/Documents/work life/Kew/large folders/plant_occurence_vars/outputs/cleaned_vari_occurences.csv')

occ_df_with_duplicates = rbind(species_df,subspecies_df)
occ_df_with_duplicates = rbind(occ_df_with_duplicates,varis_df)

occ_df = dplyr::distinct(occ_df_with_duplicates, gbifID, .keep_all = TRUE)

append_var_to_df <- function(df,reaggragated_raster){
  var_values = data.frame(extract(stack(reaggragated_raster), df[, c("decimalLongitude", "decimalLatitude")]))
  bound_df = cbind(df, var_values)
  
  return(bound_df)
}


for (r in prepared_rasters){
  print(names(r))
  occ_df<-append_var_to_df(occ_df,r)
}

write.csv(occ_df, '/home/atp/Documents/work life/Kew/large folders/occ_climate_vars/occ_with_climate_vars.csv')
