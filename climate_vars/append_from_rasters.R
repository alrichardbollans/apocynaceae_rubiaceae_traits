library(raster)

import_raster <- function(filename){
  str_name<-paste('/home/atp/Downloads/rasters/',filename,sep='')
  imported_raster=raster(str_name)
  return(imported_raster)
}

append_var_to_df <- function(df,file_name){
  x = import_raster(file_name)
  var_values = data.frame(extract(stack(x), df[, c("decimalLongitude", "decimalLatitude")]))
  bound_df = cbind(df, var_values)
  
  return(bound_df)
}

# Get dataframe containing cleaned occurences
species_df = read.csv(file.path('inputs','cleaned_species_occurences.csv'))

species_df<-append_var_to_df(species_df,'CHELSA_bio1_1981-2010_V.2.1.tif')
species_df<-append_var_to_df(species_df,'CHELSA_bio12_1981-2010_V.2.1.tif')
species_df<-append_var_to_df(species_df,'nitrogen_0-5cm_mean.tif')
species_df<-append_var_to_df(species_df,'phh2o_0-5cm_mean.tif')
write.csv(species_df, file.path('temp_outputs','species_with_clim_vars.csv'))

