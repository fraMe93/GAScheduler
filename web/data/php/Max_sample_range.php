<?php
			require 'connection.php';
			$deviceid=$_GET["id"];
			$id_run=$_GET["id_run"];
			$query="SELECT template from device_list where device_id=".$deviceid." ";
			$res = mysqli_query($con,$query) or die("BAD SQL");
			$obj=mysqli_fetch_object($res);
			$idtemplate= $obj->template;
			//echo 'prova';
		
		//selezione del number massimo di ogni idtemplate e id run
			$query2="select MAX(samples.number) from samples where template=$idtemplate and run_ID='".$id_run."' ";
			$res2 = mysqli_query($con,$query2) or die("BAD SQL");
			$row2 = mysqli_fetch_array($res2);
			$sample_n=$row2[0];
			$num_max_sample_chart=$sample_n*60;
			//echo $num_max_sample_chart;
			echo json_encode($num_max_sample_chart);
		//Number del campione maggiore per quel template mi serve per regolare la scala sul grafico
		
?>
