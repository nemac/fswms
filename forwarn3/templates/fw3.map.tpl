MAP
    # the following two lines tell MapServer to write debugging output to a log file.  Remove the '#' from the beginning
    # of the two lines below to enable this logging:
    #CONFIG "MS_ERRORFILE" "%(MS_ERRORFILE)s"
    #DEBUG 5

    # all temp files get prefixed with this string
    NAME %(TEMP_FILE_PREFIX)s

    # background color of image if transparency
    # is not requested
    IMAGECOLOR 255 255 255

    # default output image dimensions
    SIZE 600 400
	  MAXSIZE 4000
    # always returns a map
    STATUS ON

    # set top level projection
    PROJECTION
     {projection}
    END

    # image format options
    OUTPUTFORMAT
     NAME png
     DRIVER "GD/PNG"
     MIMETYPE "image/png"
     IMAGEMODE RGB
     EXTENSION "png"
    END

    OUTPUTFORMAT
      NAME "GEOTIFF"
      DRIVER "GDAL/GTiff"
      MIMETYPE "image/tiff"
      IMAGEMODE "BYTE"
      EXTENSION "tif"
    END

    # minx miny maxx maxy
    # sets:
    # /WMT_MS_Capabilities/Capability/Layer/LatLonBoundingBox(@minx @miny @maxx @maxx)
    EXTENT -180 -90 180 90 # World

    # add def pointers for symbols
    SYMBOLSET "./symbols/symbols35.sym"
    FONTSET   "./fonts/fonts.list"

    #
    # Start of web interface definition
    WEB
        # this is the real filepath to the temp dir for intermediate file creation
        IMAGEPATH "./tmp"
        # this is the web-accessible path to IMAGEPATH
        IMAGEURL "/tmp/"
        HEADER "./templates/query_header.html"
        FOOTER "./templates/query_footer.html"
        METADATA
            "ows_enable_request"     "*"
            "wms_title"              "{ows_title}"
            "wms_abstract"           "{ows_abstract}"
            "wms_onlineresource"     "{service_url}"
            "wms_srs"                "{wms_srs}"
            "wcs_label"              "{wcs_label}"
            "wcs_srs"                "EPSG:2163"
            "ows_contactorganization" "UNCA's NEMAC"
        END
    END

    QUERYMAP
        STATUS OFF
    END

    LEGEND
      STATUS ON
      LABEL
        COLOR 0 0 0
        FONT "vera_serif"
        TYPE truetype
        SIZE 9
        POSITION cl
      END
    END

    {layers}

END # end MAP
