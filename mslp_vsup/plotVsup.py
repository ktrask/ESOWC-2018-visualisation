#importing Magics module
from Magics.macro import *

png = output(output_name_first_page_number = "off",
   output_formats=['pdf'],
   output_name="SoC-netcdf"
)

vsup_data = mnetcdf(
  netcdf_filename = "vsup.nc",
  netcdf_value_variable = "Vsup"
)

vsup_contour =  mcont(  contour_level_selection_type = "level_list",
                        contour_shade_colour_method = "list",
                        contour_legend_text = "WWW Style",
                        contour_shade_method = "area_fill",
                        contour_shade = "on",
                        contour_level_list =  [0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.],
                        contour_shade_max_level = 14,
                        contour_reference_level = 0,
                        contour_hilo = "off",
                        contour_label =  "off",
                       # contour_shade_min_level =  0,
                        contour = "off",
                        contour_shade_colour_list = [   "rgb(84,0,108)",
                                                        "rgb(78,41,135)",
                                                        "rgb(56,91,142)",
                                                        "rgb(0,131,142)",
                                                        "rgb(0,168,134)",
                                                        "rgb(0,202,111)",
                                                        "rgb(91,230,63)",
                                                        "rgb(201,244,0)",
                                                        "rgb(125,73,156)",
                                                        "rgb(100,143,169)",
                                                        "rgb(78,205,156)",
                                                        "rgb(179,245,98)",
                                                        "rgb(159,156,196)",
                                                        "rgb(163,239,172)",
                                                        "rgb(200,228,225)"]
                )


#plot(png,  spread_data, spread_contour, mean_data, mean_contour, mcoast(), )
plot(png,vsup_data, vsup_contour, mcoast())
