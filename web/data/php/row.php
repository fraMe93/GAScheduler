<?php
			require '../php/connection.php';
                        //query template types
			$deviceids=$_GET["ids"];
			$id_arr = explode("*", $deviceids);
			foreach ($id_arr as $id){
				if (strlen($id) > 0){
					//echo(strlen($id));
					//echo $id;
					$query_inst="SELECT MAX(instance) from device where template=" . $id . ";";
					$res_inst = mysqli_query($con,$query_inst) or die("BAD SQL");
					$value = mysqli_fetch_row($res_inst);
					$counter=$value[0]+1;
					
					$query="SELECT * from template where dev_id=" . $id . ";";
					$res = mysqli_query($con,$query) or die("BAD SQL2");
					$num_righe=mysqli_num_rows($res);
					for($i=0;$i<$num_righe;$i++) {
						$row = mysqli_fetch_array($res);	
						echo '{instance: "' . $counter . '", temp_id: ' . $row[0] . ', 
						name: "' . $row[1] . '", type: "' . $row[3] . '", class: "' . $row[2] . '"}';
					}
				}
			}
				
?>
