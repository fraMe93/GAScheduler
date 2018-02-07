<?php
			require '../php/connection.php';
                        //query template types
			$deviceid=$_POST["id"];
			$count=$_POST["count"];
			$query_inst="SELECT max(instance) from device where template=" . $deviceid . ";";
			$res_inst = mysqli_query($con,$query_inst) or die("BAD SQL");
			$value = mysqli_fetch_row($res_inst);
			if(isset($value))
				$counter=$value[0]+$count;
			else
				$counter = $count;
			$query="SELECT * from template where dev_id=" . $deviceid . ";";
			$res = mysqli_query($con,$query) or die("BAD SQL");
			$row = mysqli_fetch_row($res);
			//$counter . $row[0] . '*' . 	
			echo $counter . '*' . $row[0] . '*' . $row[1] . '*' . $row[3] . '*' . $row[2];
					
mysqli_close($con);
				
?>
    
    
</rows>
