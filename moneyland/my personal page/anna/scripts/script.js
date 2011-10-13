// JavaScript Document
function init(){
	document.getElementsByName('email').item(0).onfocus = function() {
			if(document.getElementById('hd').value == "ru"){
				if(this.value == "Ваш e-mail"){this.value = ""}}
			else{
				if(this.value == "Your e-mail"){this.value = ""}}
		}
	document.getElementsByName('email').item(0).onblur = function() {
			if(document.getElementById('hd').value == "ru"){
				if(this.value == ""){this.value = "Ваш e-mail"}}
			else{
				if(this.value == ""){this.value = "Your e-mail"}}
		}	
		
	document.getElementsByName('text').item(0).onfocus = function() {
			if(document.getElementById('hd').value == "ru"){
				if(this.value == "Текст сообщения"){ this.value = ""}}
			else{
				if(this.value == "Your message"){ this.value = ""}}
		}	
	document.getElementsByName('text').item(0).onblur = function() {
			if(document.getElementById('hd').value == "ru"){
				if(this.value == ""){this.value = "Текст сообщения"}}
			else{
				if(this.value == ""){this.value = "Your message"}}
		}
	document.getElementsByName('send').item(0).onmouseover = function() {this.style.backgroundPosition = "bottom"} 
	document.getElementsByName('send').item(0).onmouseout = document.getElementsByName('send').item(0).onclick = function() {this.style.backgroundPosition = "top"} 	
}