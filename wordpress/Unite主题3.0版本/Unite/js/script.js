$(document).ready(function(){

// 搜索
$(".nav-search").click(function(){
	$("#main-search").slideToggle(500);
});
	
// 去边线
$(".message-widget li:last, .message-page li:last, .hot_commend li:last, .random-page li:last, .search-page li:last, .my-comment li:last").css("border","none");

// 表情
$('.smiley').click(function () {
	$('.smiley-box').animate({
		opacity: 'toggle',
		left: '50px'
	}, 1000).animate({
		left: '10px'
	}, 'fast');
	return false;
});

// 文字展开
$(".showmore span").click(function(e){
	$(this).html(["▼显示", "▲隐藏"][this.hutia^=1]);
	$(this.parentNode.parentNode).next().slideToggle();
	e.preventDefault();
});

// 弹窗
$('#share-main-s').leanModal({
	top: 110,
	overlay: 0.6,
	closeButton: '.hidemodal'
});
	$('#shang-main-p').leanModal({
	top: 50,
	overlay: 0.6,
	closeButton: '.hidemodal'
});
});
// 文字滚动
(function($){$.fn.textSlider=function(settings){settings=jQuery.extend({speed:"normal",line:2,timer:1000},settings);return this.each(function(){$.fn.textSlider.scllor($(this),settings)})};$.fn.textSlider.scllor=function($this,settings){var ul=$("ul:eq(0)",$this);var timerID;var li=ul.children();var _btnUp=$(".up:eq(0)",$this);var _btnDown=$(".down:eq(0)",$this);var liHight=$(li[0]).height();var upHeight=0-settings.line*liHight;var scrollUp=function(){_btnUp.unbind("click",scrollUp);ul.animate({marginTop:upHeight},settings.speed,function(){for(i=0;i<settings.line;i++){ul.find("li:first").appendTo(ul)}ul.css({marginTop:0});_btnUp.bind("click",scrollUp)})};var scrollDown=function(){_btnDown.unbind("click",scrollDown);ul.css({marginTop:upHeight});for(i=0;i<settings.line;i++){ul.find("li:last").prependTo(ul)}ul.animate({marginTop:0},settings.speed,function(){_btnDown.bind("click",scrollDown)})};var autoPlay=function(){timerID=window.setInterval(scrollUp,settings.timer)};var autoStop=function(){window.clearInterval(timerID)};ul.hover(autoStop,autoPlay).mouseout();_btnUp.css("cursor","pointer").click(scrollUp);_btnUp.hover(autoStop,autoPlay);_btnDown.css("cursor","pointer").click(scrollDown);_btnDown.hover(autoStop,autoPlay)}})(jQuery);

// 表情
function grin(a){var d;a=" "+a+" ";if(document.getElementById("comment")&&document.getElementById("comment").type=="textarea"){d=document.getElementById("comment")}else{return false}if(document.selection){d.focus();sel=document.selection.createRange();sel.text=a;d.focus()}else{if(d.selectionStart||d.selectionStart=="0"){var c=d.selectionStart;var b=d.selectionEnd;var e=b;d.value=d.value.substring(0,c)+a+d.value.substring(b,d.value.length);e+=a.length;d.focus();d.selectionStart=e;d.selectionEnd=e}else{d.value+=a;d.focus()}}};

// 弹窗
(function(a){a.fn.extend({leanModal:function(d){var e={top:100,overlay:0.5,closeButton:null};var c=a("<div id='overlay'></div>");a("body").append(c);d=a.extend(e,d);return this.each(function(){var f=d;a(this).click(function(j){var i=a(this).attr("href");a("#overlay").click(function(){b(i)});a(f.closeButton).click(function(){b(i)});var h=a(i).outerHeight();var g=a(i).outerWidth();a("#overlay").css({"display":"block",opacity:0});a("#overlay").fadeTo(200,f.overlay);a(i).css({"display":"block","position":"fixed","opacity":0,"z-index":11000,"left":50+"%","margin-left":-(g/2)+"px","top":f.top+"px"});a(i).fadeTo(200,1);j.preventDefault()})});function b(f){a("#overlay").fadeOut(200);a(f).css({"display":"none"})}}})})(jQuery);
