<?php
			require '../php/connection.php';
			$name = $_POST['name'];
			$tuples = $_POST['tuples'];
			$tuples_arr = explode("@", $tuples);
			$sql = "INSERT INTO neigh (name) VALUES ('".$name."');";
			$last_id = '';
			if (mysqli_query($con, $sql)) {
				$last_id = mysqli_insert_id($con);
			}
			foreach ($tuples_arr as $tuple){
				$tuple_arr = explode("*", $tuple);
				$sql2 = "INSERT INTO device (template, instance) VALUES (".$tuple_arr[1].", ".$tuple_arr[0].");";
				$sql3 = "INSERT INTO composition (dev_template, neigh_id, dev_inst) VALUES (".$tuple_arr[1].", ".$last_id.", ".$tuple_arr[0].");";
				mysqli_query($con, $sql2);
				mysqli_query($con, $sql3);
			}

    


mysqli_close($con);
?>
