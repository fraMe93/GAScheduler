<?php 
			//superclass
			$con=mysqli_connect("localhost","root","Eequ9beuf9pe","trials") or die(mysqli_connect_error());
			$query1="SELECT  classes.name,classes.id from classes;";
			$res1 = mysqli_query($con,$query1) or die("BAD SQL");
			$num_righe1=mysqli_num_rows($res1);
echo '<html><head></head><body><p id="0">	
	<p id = "1">Products';
				for($i=0;$i<$num_righe1;$i++) {
					$row1 = mysqli_fetch_array($res1);	
					//row1[0] contiene il nome class , row1[1] contiene ID class
					echo '<p  id="tt'.$row1[1].'">'.$row1[0];
						///device for each class
							$query2="select device_list.name, device_list.device_id from device_list,device_type,templates WHERE device_type.superclassid='".$row1[1]."' AND device_type.id = templates.type and templates.id = device_list.template;";
							$res2 = mysqli_query($con,$query2) or die("BAD SQL");
							$num_righe2=mysqli_num_rows($res2);
							for($j=0;$j<$num_righe2;$j++) {
								$row2 = mysqli_fetch_array($res2);
								//row2[1] contiene id del device (mi serve per usare la funz del doubleClick nel tree)
								echo '<p id="'.$row2[1].'">' .$row2[0].'</p>';
							}
			
					echo '</p>';
				}echo '</p>	
	
</p></body></html>';	
	
			?>
