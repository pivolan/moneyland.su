<?php 
$mailto = "";
$dhost="localhost";
$duser="izhgkru_owner";
$dpass="9Sur(4/Adn*2";
$dname="izhgkru_apartments";
$aDBLink = mysql_connect($dhost, $duser, $dpass) or die("Cannot connect to the database");
mysql_select_db($dname) or die("Could not select database");
?>
