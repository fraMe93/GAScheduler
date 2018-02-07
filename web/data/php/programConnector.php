<?php 
require_once("../../codebase/connector/connector-php-master/codebase/combo_connector.php");
$res=mysql_connect("localhost","root","Eequ9beuf9pe");
mysql_select_db("max_trials");
$temp_id = $_GET['template'];
$data = new ComboConnector($res, "MySQL");
//$data->render_table("profile", "mode", "mode");
$sql = "SELECT distinct(mode) FROM profile where temp_id=" . $temp_id;
$data->render_sql($sql,"mode","mode");
?>
