// JavaScript Document
function setpass(){
	if(document.getElementById('password').value == 'Password'){
		if (/MSIE (5\.5|6)/.test(navigator.userAgent)){
			document.getElementById('changepass').innerHTML = "<input type='password' name='password' id='password' value='' onfocus='setpass();' onblur='unsetpass();' />";
			document.getElementById('password').focus(); document.getElementById('password').focus();
		}
		else{	
			document.getElementById('password').value = '';document.getElementById('password').type = 'password';	
			if(Op=/^function \(/.test([].sort))
				document.getElementById('password').focus();
		}
	}
}

function unsetpass(){
	if(document.getElementById('password').value == ''){
		if (/MSIE (5\.5|6)/.test(navigator.userAgent))
			document.getElementById('changepass').innerHTML = "<input type='text' name='password' id='password' value='Password' onfocus='setpass();' onblur='unsetpass();' />";
		else{
			document.getElementById('password').value = 'Password'; document.getElementById('password').type = 'text';		
		}
	}
}

function setlog(){
	if(document.getElementById('login').value == '')
		document.getElementById('login').value = 'Login'; 
	else	
		if(document.getElementById('login').value == 'Login'){
			document.getElementById('login').value = ''; 
		}
}