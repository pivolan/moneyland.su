<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Админка</title>
</head>
<?php 
$dhost="localhost";
$duser="ruswebm_owner";
$dpass="RhYfjkspo";
$dname="ruswebm_mail";
$aDBLink = mysql_connect($dhost, $duser, $dpass) or die("Cannot connect to the database");
mysql_select_db($dname) or die("Could not select database");
?>
<?php
if($_POST["email"]){
$result=mysql_query("SELECT id FROM mail WHERE email=\"".$_POST["email"]."\"");
if(!mysql_num_rows($result)){
	mysql_query("INSERT INTO mail (email) VALUES('".$_POST["email"]."')");
}
}
?>
<body>
<form name="mail" method="post" enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF']."#" ?>">
	Введи e-mail для рассылки <input type="text" name="email" /> <input type="submit" value="записать" />
</form>
<?php
$result=mysql_query("SELECT email FROM mail");
if($line=mysql_fetch_array($result)){
	echo "<table>";
	do{
		echo "<tr><td>$line[email]</td></tr>";
	}while($line=mysql_fetch_array($result));
	echo "</table>";
}
?>
</body>
</html>
