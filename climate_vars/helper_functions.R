summarise_raster <- function(r){
  print(r)
  print('Names:')
  print(names(r))
  print('Minmax:')
  print(minmax(r))
  print('Res:')
  print(res(r))
}

mode_fn <- function(x){
  # Get modes without NAs and use pick randomly from ties
  modes = c(statip::mfv(x, na_rm=TRUE))
  if(length(modes)==1){
    return(modes)
  }
  else{
    return(sample(modes,size = 1))
  }
  
}