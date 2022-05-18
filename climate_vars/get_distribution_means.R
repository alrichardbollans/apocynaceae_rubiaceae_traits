library(dplyr)
source(here::here('helper_functions.R'))
shp_dir = file.path('inputs','wgsrpd-master','level3')


# Read polygon feature class shapefile
# If reading a shapefile, the data source name (dsn= argument) is
# the folder (directory) where the shapefile is, 
# and the layer is the name of the shapefile (without the .shp extension)
shape_data <- rgdal::readOGR(dsn=shp_dir,layer='level3')


read_rasters <- function(){
  prep_rasters=list()
  raster_files = list.files(path=file.path('temp_outputs','prepared rasters'), pattern='*.tiff$')
  for (r in raster_files){
    print(r)
    prepped_raster = raster::raster(file.path('temp_outputs','prepared rasters',r))
    prep_rasters[[length(prep_rasters)+1]]<-prepped_raster
  }
  return(prep_rasters)
}

extract_distribution_means_to_df <- function(df, r){
  r.vals = raster::extract(r,shape_data,fun=mean, na.rm=TRUE)
  # Use list apply to calculate mean for each polygon
  r.mean <- unlist(lapply(r.vals, FUN=mean, na.rm=TRUE)) 
  
  # Join mean values to polygon data
  var_values <- data.frame(shape_data@data, placeholder_name=r.mean)
  names(var_values)[names(var_values) == "placeholder_name"] <- names(r)[[1]]
  var_values <- var_values %>% select(names(r)[[1]])
  bound_df = cbind(df, var_values)
  
  return(bound_df)
}
prepared_rasters= read_rasters()





# Do kg first
prepared_rasters = read_rasters()
kg_rast = raster::raster(file.path('temp_outputs','prepared rasters','Beck_KG_V1_present.tiff'))
kg_rast.vals = raster::extract(kg_rast,shape_data)
# Use list apply to calculate mean for each polygon
kg_rast.mode <- unlist(lapply(kg_rast.vals, FUN=mode_fn)) 

# Join mean values to polygon data
var_df <- data.frame(shape_data@data, placeholder_name=kg_rast.mode)
names(var_df)[names(var_df) == "placeholder_name"] <- names(kg_rast)[[1]]

# Do lat long
centres <- rgeos::gCentroid(shape_data, byid = TRUE)@coords
var_df = cbind(var_df, centres)
names(var_df)[names(var_df) == "x"] <- 'longitude'
names(var_df)[names(var_df) == "y"] <- 'latitude'

# Do mean values
for (r in prepared_rasters){
  if(names(r)[[1]] != 'Beck_KG_V1_present'){
    print(names(r)[[1]])
    var_df<-extract_distribution_means_to_df(var_df,r)
  }
  
}

names(var_df)[names(var_df) == "LEVEL3_COD"] <- 'tdwg3_codes'

# Get lat long
write.csv(var_df, file.path('outputs','mean_regional_bioclimatic_vars.csv'))
