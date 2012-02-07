	<wmsLayer 
	   lid="AIA"
	   visible="false" 
	   url="http://torka.unl.edu:8080/cgi-bin/mapserv.exe?map=/ms4w/apps/dm/service/usdm%(yr)s_wms.map&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=usdm%(yr)s&WIDTH=640&HEIGHT=480&srs=EPSG:4326&styles=default&format=image/png&bbox=-165,15,-60,80&TRANSPARENT=true"
	   srs="EPSG:900913" 
	   layers="usdm%(yr)s" 
	   styles="default"
	   identify="false" 
	   name="%(YR)s Drought Monitor" 
	   legend="http://dev.nemac.org/~derek/fswms/html/../msconfig/cmapicons/drought-monitor.png" />