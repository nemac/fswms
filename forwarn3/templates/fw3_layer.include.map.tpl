    LAYER
        NAME {layer_id}
        PROJECTION
{proj}
        END
        TYPE     RASTER
        DUMP     TRUE
        STATUS   OFF
        DATA     {path}
        HEADER   ./templates/layer_query_header.html
        TEMPLATE ./templates/layer_query_body.html
        GROUP {group}
        INCLUDE {color_map}
        METADATA
            "wms_title"             "{wms_title}"
      	    "wms_extent"            "{wms_extent}"
            "wms_abstract"          "{wms_abstract}"
            "wcs_label"             "{wms_title}"
            "wcs_rangeset_name"     "{wms_title}"
            "wcs_rangeset_label"    "{wcs_rangeset_label}"
            "wcs_bandcount"         "{wcs_bandcount}"
            "wcs_formats"           "{wcs_formats}"
            "wcs_nativeformat"      "{wcs_nativeformat}"
            "gml_include_items"     "{gml_include_items}"
        END
    END


