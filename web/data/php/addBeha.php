<?php
			require '../php/connection.php';
			$name = $_POST['name'];
			$neigh = $_POST['neigh'];
			$rows = $_POST['rows'];
			$rows_arr = explode("@", $rows);
			$sql = "INSERT INTO behaviour (name, neigh, time_window) VALUES ('".$name."',".$neigh.",24);";
			mysqli_query($con, $sql);
			$bid = mysqli_insert_id($con);
			$config_num = 1;
			foreach ($rows_arr as $row){
				$row_arr = explode("*", $row);
				if($row_arr[2]==1){
					$sql2 = "INSERT INTO config (num, beh_id, dev_id) VALUES (".$config_num.",".$bid.",".$row_arr[1].");";
					mysqli_query($con, $sql2);
					$config_num++;
				}
				$sql_prof="SELECT type from profile where temp_id=" . $row_arr[1] . " and model='run' and id=" . $row_arr[4] . ";";
				$res_prof = mysqli_query($con,$sql_prof) or die("BAD SQL");
				$type = mysqli_fetch_row($res_prof);

				$sql3 = "INSERT INTO task (num, conf_num, conf_temp, conf_behave, dev_inst, dev_temp, prof_temp, prof_id, prof_type, prof_model) VALUES (".$row_arr[2].", ".($config_num - 1).",".$row_arr[1].",".$bid.",".$row_arr[0].",".$row_arr[1].",".$row_arr[1].",".$row_arr[4].",'".$type[0]."','".$row_arr[3]."');";
				
				mysqli_query($con, $sql3);
				$last_id = mysqli_insert_id($con);
				$sql4 = "INSERT INTO task_parameters (task_id, name, value) VALUES (".$last_id.", 'multiplicity', '".$row_arr[7]."');";
				$sql5 = "INSERT INTO task_parameters (task_id, name, value) VALUES (".$last_id.", 'EST_data', '".$row_arr[8]."');";
				
				mysqli_query($con, $sql4);
				mysqli_query($con, $sql5);
			}

mysqli_close($con);
?>
