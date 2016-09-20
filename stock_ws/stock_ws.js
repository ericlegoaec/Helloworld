var ws;
var prod = "HSIU";

var Type_GetNow="GN";
var Type_GetMinNowData="GMN";
var Type_GetMinAllData="GMA";
var Type_GetLast="GL";
var Type_GetPic200="GP";
var Type_GetDaily="GD";
var Type_GetIndex="GIN";
var Type_Clear="Clear";
var Type_ModifyData="MD";

function getLast(){
	var d = new Date();
	//minDate=d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate();
	var hh=d.getHours();
	var mm=d.getMinutes();
	var ss=d.getSeconds();
	if(hh<10)hh="0"+hh;
	if(mm<10)mm="0"+mm;
	if(ss<10)ss="0"+ss;
	ch_country(hh+":"+mm+":"+ss)

	financeData=new Object();
	var dataProd=new Array();	
	var quote=new Object();
	financeData["quote"]=quote;
	financeData["mins"]=dataProd;
	MaxP=0;
	MinP=9999999;
	MaxPBar=0;
	MinPBar=9999999;
	LoginClass.pickupData=new Array();
	//ws.send('{"t":"'+Type_GetLast+'","p":"IF300"}');

	//console.log("prod",prod)
	ws.send('{"t":"'+Type_GetLast+'","p":"'+prod+'"}');
}

function init() {

	ws = new WebSocket('ws://119.9.24.48:5490');	

	ws.onopen = function() {
		//console.log('open');
		//ws.send('Hello')  // Sends a message.
		err_cnt=0;
		getLast();
	}
}