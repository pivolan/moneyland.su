// JavaScript Document
function kp(event) {
	event = (event) ? event : window.event;
	if (event.keyCode == 13 ) document.getElementById('autorization').submit();
}

function SwitchImage() {
    if (document.getElementById('checkbox').checked == true) {
        document.getElementById('checkbox').checked = false;
        document.getElementById('foncheckbox').style.background = 'url(/images/unchecked.gif) left top no-repeat';
    } else {
        document.getElementById('checkbox').checked = true;
		document.getElementById('foncheckbox').style.background = 'url(/images/checked.gif) left top no-repeat';
	}
}

function init() {
	document.getElementById("checkboxman").checked = true;
	document.getElementById("mans").style.background = "url(/images/checked.gif) left top no-repeat";
	document.getElementById("checkboxwoman").checked = false;
	document.getElementById("womans").style.background = "url(/images/unchecked.gif) left top no-repeat";
}

function SwitchSex() {
    if (document.getElementById("checkboxman").checked == true) {
        document.getElementById("checkboxman").checked = false;
		document.getElementById("checkboxwoman").checked = true;
        document.getElementById("mans").style.background = "url(/images/unchecked.gif) left top no-repeat";
		document.getElementById("womans").style.background = "url(/images/checked.gif) left top no-repeat";
    } else {
        document.getElementById("checkboxman").checked = true;
		document.getElementById("checkboxwoman").checked = false;
		document.getElementById("mans").style.background = "url(/images/checked.gif) left top no-repeat";
		document.getElementById("womans").style.background = "url(/images/unchecked.gif) left top no-repeat";
	}
}

function AllSel() {
    if (document.getElementById('allcheckbox').checked == true) {
        document.getElementById('allcheckbox').checked = false;
        document.getElementById('fonallcheck').style.background = 'url(/images/mailsel.gif) top no-repeat';
		$("input[name*='checkbox']").attr('checked',false);
		$("div.foncheck").css('background','url(/images/mailsel.gif) top no-repeat');
    } else {
        document.getElementById('allcheckbox').checked = true;
		document.getElementById('fonallcheck').style.background = 'url(/images/mailsel.gif) bottom no-repeat';
		$("input[name*='checkbox']").attr('checked',true);
		$("div.foncheck").css('background','url(/images/mailsel.gif) bottom no-repeat');
	}
}

function SelCheck(n, obj) {
	if (document.getElementById('checkbox'+n).checked == true) {
        document.getElementById('checkbox'+n).checked = false;
        document.getElementById('allcheckbox').checked = false;
		document.getElementById('fonallcheck').style.background = 'url(/images/mailsel.gif) top no-repeat';
        obj.style.background = 'url(/images/mailsel.gif) top no-repeat';
    } else {
        document.getElementById('checkbox'+n).checked = true;
		obj.style.background = 'url(/images/mailsel.gif) bottom no-repeat';
	}
}

function clearform(){
	document.profile.username.value = '';
	document.profile.first_name.value = '';
	document.profile.password.value = '';
	document.profile.confirm.value = '';
	document.profile.email.value = '';
	document.profile.skype.value = '';
	document.profile.icq.value = '';
	document.profile.phone.value = '';
	document.profile.wme.value = '';
	document.profile.yad.value = '';
	document.profile.liqpay.value = '';
	if(document.profile.yes.checked) SwitchImage();
}

function clearmailform(){
	document.sentmail.address.value = '';
	document.sentmail.theme.value = '';
	document.sentmail.textmail.innerHTML = '';
	document.sentmail.textmail.value = '';
}
function checkLogin(){ 
	document.getElementById("td_username").innerHTML = "<img src='/images/ajax-loader.gif'/>";
	$.getJSON("", {'username':document.profile.username.value}, function(data){
		document.getElementById("td_username").innerHTML = '<span>' + data.username + '</span>';
	})
}
function SetNumbers(n1,n2){
	document.getElementById("numbers1").innerHTML ='';
	document.getElementById("numbers2").innerHTML ='';
	
	if(n1>=0){
		do{
			switch(n1%10){
				case 0: document.getElementById("numbers1").innerHTML += '<div class="zero"></div>'; break;
				case 1: document.getElementById("numbers1").innerHTML += '<div class="one"></div>'; break;
				case 2: document.getElementById("numbers1").innerHTML += '<div class="two"></div>'; break;
				case 3: document.getElementById("numbers1").innerHTML += '<div class="three"></div>'; break;
				case 4: document.getElementById("numbers1").innerHTML += '<div class="four"></div>'; break;
				case 5: document.getElementById("numbers1").innerHTML += '<div class="five"></div>'; break;
				case 6: document.getElementById("numbers1").innerHTML += '<div class="six"></div>'; break;
				case 7: document.getElementById("numbers1").innerHTML += '<div class="seven"></div>'; break;
				case 8: document.getElementById("numbers1").innerHTML += '<div class="eight"></div>'; break;
				case 9: document.getElementById("numbers1").innerHTML += '<div class="nine"></div>'; break;}
			n1/=10;	
		}while(n1-=n1%1)}
	if(n2>=0){				
		do{
			switch(n2%10){
				case 0: document.getElementById("numbers2").innerHTML += '<div class="zero"></div>'; break;
				case 1: document.getElementById("numbers2").innerHTML += '<div class="one"></div>'; break;
				case 2: document.getElementById("numbers2").innerHTML += '<div class="two"></div>'; break;
				case 3: document.getElementById("numbers2").innerHTML += '<div class="three"></div>'; break;
				case 4: document.getElementById("numbers2").innerHTML += '<div class="four"></div>'; break;
				case 5: document.getElementById("numbers2").innerHTML += '<div class="five"></div>'; break;
				case 6: document.getElementById("numbers2").innerHTML += '<div class="six"></div>'; break;
				case 7: document.getElementById("numbers2").innerHTML += '<div class="seven"></div>'; break;
				case 8: document.getElementById("numbers2").innerHTML += '<div class="eight"></div>'; break;
				case 9: document.getElementById("numbers2").innerHTML += '<div class="nine"></div>'; break;}
			n2/=10;
		}while(n2-=n2%1)}
}
$(document).ready(function(){              // по окончанию загрузки страницы
    if (document.getElementById('checkbox').checked == true) {
		SwitchImage();
		SwitchImage();
	}
});   //document ready end