<?php
			require '../php/connection.php';
			
			$query_inst="SELECT * from neigh;";
			$res_inst = mysqli_query($con, $query_inst);
			$num_righe=mysqli_num_rows($res_inst);
			$response = "";
				for($i=0;$i<$num_righe;$i++) {
					$row = mysqli_fetch_array($res_inst);	
					if(strlen($response)<1){
						$response = $row[0] . "*" . $row[1];
					}
					else{
						$response = $response . "@" . $row[0] . "*" . $row[1];
					}
				}
			echo $response;
    


mysqli_close($con);
?>
