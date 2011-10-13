// JavaScript Document
function Clear(){
	document.message.name.value = "";
	document.message.email.value = "";
	document.message.text.value = "";
	document.message.text.innerHTML = "";
}

function SelCheck(obj) {
	if (document.getElementById('checkbox').checked == true) {
        document.getElementById('checkbox').checked = false;
        obj.style.background = 'url(../images/mailsel.gif) top no-repeat';
    } else {
        document.getElementById('checkbox').checked = true;
		obj.style.background = 'url(../images/mailsel.gif) bottom no-repeat';
	}
}
