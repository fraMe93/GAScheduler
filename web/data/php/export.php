<?php
			require '../php/connection.php';
			$bid = $_POST['bid'];
			if (!file_exists('../../behaviours/B' . $bid)) {
    				mkdir('../../behaviours/B' . $bid, 0777, true);
			}
			$query="SELECT id, num, dev_inst, dev_temp, conf_behave, prof_id, prof_model from task where conf_behave=" . $bid . ";";
			$res = mysqli_query($con,$query) or die("BAD SQL");
			$num_righe=mysqli_num_rows($res);
			for($i=0;$i<$num_righe;$i++) {
				$lines="";
				$row = mysqli_fetch_array($res);
				$query_temp="SELECT name, type, class from template where dev_id=" . $row[3] . ";";
				$res_temp = mysqli_query($con,$query_temp) or die("BAD SQL");
				$temp = mysqli_fetch_row($res_temp);
				$panel = false;
				if ($temp[2] === "pv") $panel = true;
				$midnightOffset = 0;
				if (!file_exists('../../behaviours/B' . $bid . "/" . $temp[1])) {
    					mkdir('../../behaviours/B' . $bid . "/" . $temp[1], 0777, true);
				}
				
				$query_run="SELECT formula, start, stop from profile where temp_id=" . $row[3] . " and id=" . $row[5] . " and model='" . $row[6] . "';";
				$res_run = mysqli_query($con,$query_run) or die("BAD SQL");
				$ts = mysqli_fetch_row($res_run);
				// open the input and the output
				
				$file = json_decode($ts[0], true);
				$fileName = $file["filename"];
				$lines = file($_SERVER["DOCUMENT_ROOT"] . "/Configurator/timeseries/" . $fileName);//file in to an array
				$date = explode(" ", $lines[$ts[1]]);
				$DAdate = date('Y/m/d H:i:s',  $date[0]);
				$finDate = str_replace("/","_",$DAdate);
				$finDate = str_replace(" ","_",$finDate);
				$finDate = str_replace(":","_",$finDate);
				if($panel){
					$prepoffH = date('H', $date[0]);$prepoffM = date('i', $date[0]);$prepoffS = date('s', $date[0]);
					$midnightOffset = $prepoffH*3600 + $prepoffM*60 + $prepoffS;
				}
				$filename = '../../behaviours/B' . $bid . "/" . $temp[1] . "/B" . $bid . "_D" . $row[2] . "_" . $temp[0] . "_T" . $row[1] . "_" . $finDate . ".csv";
				$out = fopen($filename,"wb");
				$firstline=1;
				$starttime=0;
				$prevarea=0;
				for($j=$ts[1];$j<=$ts[2];$j++){				    					
					$data = explode(" ", $lines[$j]);
					if($firstline){
						$starttime=$data[0];
						if ($panel) $time=$data[0]-$starttime+$midnightOffset;
						else $time=$data[0]-$starttime;
						$value=0;
						$firstline=0;
					}
					else{
						$prev_data=explode(" ", $lines[$j-1]);
						if ($panel) $time=$data[0]-$starttime+$midnightOffset;
						else $time=$data[0]-$starttime;
						//kWh
						$actualarea=(($data[1]+$prev_data[1])*($data[0]-$prev_data[0]))/(2*3600*1000);
						$prevarea=$prevarea+$actualarea;
						
						//$value=($prevarea/3600)/1000;
					}
					fwrite($out, $time . " " . $prevarea . "\n");
				  
				  }
				  fclose($out);
				$query_const = "SELECT name, value from task_parameters where task_id=" . $row[0] . ";";
				$res_const = mysqli_query($con,$query_const) or die("BAD SQL");
				$num_righe_const=mysqli_num_rows($res_const);
				$mult=1;
				$EST_data="";	
				for($k=0;$k<$num_righe_const;$k++) {
					$row_const = mysqli_fetch_array($res_const);
					if($row_const[0]==="multiplicity")
						$mult = $row_const[1];
					else if($row_const[0]==="EST_data")
						$EST_data = $row_const[1];
				}
				$fileconst = '../../behaviours/B' . $bid . "/" . $temp[1] . "/B" . $bid . ".constraints.csv";
				$const = fopen($fileconst,"ab");
				if($temp[1]==="consumption"){
					//these parameters should depend from the time_window
					//for now it is 24hrs so EST is 0 and LST is 86400 seconds
					$EST=0;
					$LST=86400;
					for($k=0;$k<$mult;$k++){
						if(strpos($EST_data, "rand")!== false){
							//remove rand prefix
							$subEST = substr($EST_data, 4);
							$arrdel = explode("del", $subEST);
							$intervals = $arrdel[0];
							$fixedDelay = $arrdel[1];
							$int_arr = explode("-", $intervals);
							$beginTime = $int_arr[0];
							$endTime = $int_arr[1];
							$beginTime_arr = explode(":", $beginTime);
							$endTime_arr = explode(":", $endTime);
							$beginTimeSec = $beginTime_arr[0]*3600+$beginTime_arr[1]*60;
							$endTimeSec = $endTime_arr[0]*3600+$endTime_arr[1]*60;
							$EST = rand($beginTimeSec, $endTimeSec);
							$LST=$EST+($fixedDelay*60);
						}
						else if(strpos($EST_data, "del")!== false){
							$arrdel = explode("del", $EST_data);
							$intervals = $arrdel[0];
							$interDelay = $arrdel[1];
							$int_arr = explode("-", $intervals);
							$beginTime = $int_arr[0];
							$endTime = $int_arr[1];
							$beginTime_arr = explode(":", $beginTime);
							$endTime_arr = explode(":", $endTime);
							$beginTimeSec = $beginTime_arr[0]*3600+$beginTime_arr[1]*60;
							$endTimeSec = $endTime_arr[0]*3600+$endTime_arr[1]*60;
							$EST = rand($beginTimeSec, $endTimeSec);

							$intdel_arr = explode("-", $interDelay);
							$beginDelTime = $intdel_arr[0];
							$endDelTime = $intdel_arr[1];
							$beginDelTime_arr = explode(":", $beginDelTime);
							$endDelTime_arr = explode(":", $endDelTime);
							$beginDelTimeSec = $beginDelTime_arr[0]*3600+$beginDelTime_arr[1]*60;
							$endDelTimeSec = $endDelTime_arr[0]*3600+$endDelTime_arr[1]*60;
							$delay = rand($beginDelTimeSec, $endDelTimeSec);
							$LST=$EST+$delay;
						}
						else{
							$arrs=explode("-", $EST_data);
							$EST_arr=explode(":", $arrs[0]);
							$EST = $EST_arr[0]*3600 + $EST_arr[1]*60;
							$LST_arr=explode(":", $arrs[1]);
							$LST = $LST_arr[0]*3600 + $LST_arr[1]*60;
						}
						fwrite($const, "B" . $bid . "_D" . $row[2] . "_" . $temp[0] . "_T" . $row[1] . "_" . $finDate . ".csv" . "," . $EST . "," . $LST . "\n");
					}
				}
				else{
					fwrite($const, "B" . $bid . "_D" . $row[2] . "_" . $temp[0] . "_T" . $row[1] . "_" . $finDate . ".csv" . "," . $mult . "\n");
				}
			}

mysqli_close($con);
?>
