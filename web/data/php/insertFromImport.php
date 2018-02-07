<?php
        require 'connection.php';
	$TypeName=$_GET["TypeName"];
	$TemplateName=$_GET["TemplateName"];
	$class_selected=$_GET["class_selected"];
	
	//inserimento del Nuovo type Device
	$query="INSERT INTO device_type (type,behaviour,superclassid) VALUES ('".$TypeName."','0','".$class_selected."');";
	$res = mysqli_query($con,$query) or die("BAD SQL");
	
	//selezione del id del nuovo tipo appena inserito
	$query="SELECT device_type.id FROM device_type WHERE type='".$TypeName."';";
	$res = mysqli_query($con,$query) or die("BAD SQL");
	$row = mysqli_fetch_array($res);
	$id_devType=$row[0];
	
	//inserimento del template relativo al nuovo type inserito
	$query="INSERT INTO templates (name,type) VALUES ('".$TemplateName."','".$id_devType."');";
	$res = mysqli_query($con,$query) or die("BAD SQL");
	
	
	//inserimento dei samples relativi a quel template
	// devo sapere a quale run appartengono , INDIVIDUAZIONE DELLE RUN PRIMA DI procedere all'inserimento
			
?>
