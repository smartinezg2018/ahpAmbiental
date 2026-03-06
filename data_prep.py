import h3 
import xarray as xr
import rasterio
from shapely.geometry import Polygon
import geopandas as gpd
import numpy as np
import os
import pandas as pd
from rasterstats import zonal_stats

class h3_grid:

    def __init__(self,raster,resolution,crs):
        self.raster = raster
        self.crs = crs
        self.resolution = resolution
        # sistema coordenado del raster
        self.crs_raster = raster.crs.to_string()
        # Almacena la grilla de h3
        self.grid_cache = dict()
        
    def create_polygon(self,):
        
        ext = self.raster.bounds
        up_l_corner = (ext[-1],ext[0])
        up_r_corner = (ext[-1],ext[2])
        down_l_corner = (ext[1],ext[0])
        down_r_cornor = (ext[1],ext[2])
        # Creacion poligono
        polygon = Polygon(
            (
                down_l_corner,down_r_cornor,
                up_r_corner,up_l_corner
            )
        )
        return polygon
    def get_grid(self,) -> gpd.GeoDataFrame:
        """
        Retorna la grilla H3 para una resolución dada.
        Si ya fue generada, la retorna desde caché sin recalcular.
        """
        if self.resolution not in self.grid_cache:
            self.grid_cache[self.resolution] = self.create_grid()
        return self.grid_cache[self.resolution]

    def create_grid(self):
        # Crea el poligono para h3
        polygon = self.create_polygon()
        # Crea el gdf con el h3
        hexagons = h3.geo_to_cells(
            polygon, 
            self.resolution
        )

        # Creacion geodataframe
        geometry = list()
        for h in hexagons:
            poligono = Polygon(h3.cell_to_boundary(h))
            geometry.append(poligono)
        # Geodataframe
        gdf_hex = gpd.GeoDataFrame(
            {'h3': hexagons},
            geometry=geometry,
            crs= self.crs_raster
        )
        if self.crs_raster != self.crs:
            gdf_hex = gdf_hex.to_crs(self.crs)
        # Conversion de los datos
        # gdf_hex = gdf_hex.to_crs(self.crs)
        return gdf_hex

    # Funciones para cada tipo de variable

    def var_binarias(self,gdf)-> pd.Series:

        gdf_hex = self.get_grid()
        
        if gdf_hex.crs != gdf.crs:
            gdf = gdf.to_crs(gdf_hex.crs)
    
        # 2. Realizar el Spatial Join
        # Esto asigna a cada punto el ID del hexágono donde se encuentra
        # 'predicate="within"' es lo inverso a contains, ideal para puntos dentro de polis
        puntos_con_hex = gpd.sjoin(
            gdf, 
            gdf_hex, 
            how="left"
        )
        # genera puntos de presencia
        col_binaria = gdf_hex['h3'].isin(puntos_con_hex['h3']).astype(int)
        
        return col_binaria


    def var_continuas(self,ds)->pd.Series:

        gdf_hex = self.get_grid()
        stats = zonal_stats(
            gdf_hex,
            ds.values[0],                    # array 2D
            affine=ds.rio.transform(),     # transformación geoespacial 
            nodata = np.nan,
            stats=['mean'],
        )

        # Deberia regresar el array
        array = pd.Series([s['mean'] for s in stats])

        return array

    def var_excluyentes(self,gdf) -> pd.Series:
        
        gdf_hex = self.get_grid()
        
        if gdf_hex.crs != gdf.crs:
            gdf = gdf.to_crs(gdf_hex.crs)
    
        # 2. Realizar el Spatial Join
        # Esto asigna a cada punto el ID del hexágono donde se encuentra
        # 'predicate="within"' es lo inverso a contains, ideal para puntos dentro de polis
        puntos_con_hex = gpd.sjoin(
            gdf, 
            gdf_hex, 
            how="left"
        )
        # genera puntos de presencia
        col_binaria = gdf_hex['h3'].isin(puntos_con_hex['h3']).astype(int)
        # Genera los espacios NaN donde no se hacen computos
        col_binaria = col_binaria.replace(1,np.nan)
        
        return col_binaria

    def open_var(self,path):
        """
        Lee los archivos shape o raster y los prepara para incluirlos
        geodatafrma de h3
        """
        files = os.listdir(path)

        # busca sobre los archivos y revisa si hay tif o shape
        for file in files:

            if file.endswith('.tif'):
                return xr.open_dataarray(os.path.join(path,file),engine="rasterio")

                
            elif file.endswith('.shp'):
                return gpd.read_file(os.path.join(path,file))


            
        raise Exception('Ningun archivo es shape o raster. Revise la informacion')

            

    def vars_ahp(self,path,df_data):

        # Crea la malla de h3
        gdf_hex = self.get_grid()
        
        for idx in df_data.index:

            # Extrae el codigo y tipo de dato
            cod = df_data.iloc[idx,0]
            tipo = df_data.iloc[idx,2]
            
            print(f'Empezando variable {cod}...')
            # Lectura de datos
            file_path = os.path.join(path,cod)
            data = self.open_var(file_path)

            # Clasificacion
            if tipo == 'binario':
                var_series = self.var_binarias(data) 
            elif tipo == 'continua':
                var_series = self.var_continuas(data)
            elif tipo == 'excluyente':
                var_series = self.var_excluyentes(data)
            else:
                raise Exception('Ningun archivo es shape o raster. Revise la informacion')
            # Actualiza el dataframe
            gdf_hex[cod] = var_series
                

            


        return gdf_hex 

        
        
        

        
            

    

    
    

    
