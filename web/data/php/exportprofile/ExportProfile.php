<?php

//$feedid=$_GET["feedid"];
$settings = Array();

include "PHPTimeSeries.php";
$phpts= new PHPTimeSeries($settings);
$feedid=13;
$outfile="file_CSV_".$feedid.".csv";
$phpts->exportcsv($feedid,$outfile);

echo "ok";
?>
