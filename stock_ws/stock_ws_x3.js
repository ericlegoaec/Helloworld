var minDataQty = 30000;
var getDataTimeout = 800;
var LastPrice=0;
var PriceDot=0;
var DotLength=0;
var financeData=new Object();
var modifyCount=0;
var OpenP=0;
var MaxP=0;
var MinP=9999999;
var ClosePBar=0;
var OpenPBar=0;
var MaxPBar=0;
var MinPBar=9999999;
var openTime="";
var closeTime="";
var openTimeGraph="";
var closeTimeGraph="";
var nowcount=0;
function logoutBtn(){
	localStorage.MobileSid=undefined;
	localStorage.loginAcc="";
	localStorage.loginPass="";
	logout()
}
function logout(){
	location.reload();
}




var Type_GetNow="GN";
var Type_GetMinNowData="GMN";
var Type_GetMinAllData="GMA";
var Type_GetLast="GL";
var Type_GetPic200="GP";
var Type_GetDaily="GD";
var Type_GetIndex="GIN";
var Type_Clear="Clear";
var Type_ModifyData="MD";
var ws;
//chProd("IF300",false);


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
function getAllM(){
	ws.send('{"t":"'+Type_GetMinAllData+'","p":"'+prod+'"}');
}

var err_cnt=0;
function StartWS(){
	var d = new Date();
			//minDate=d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate();
	var hh=d.getHours();
	var mm=d.getMinutes();
	var ss=d.getSeconds();
	if(hh<10)hh="0"+hh;
	if(mm<10)mm="0"+mm;
	if(ss<10)ss="0"+ss;
	ch_country(hh+":"+mm+":"+ss)
//	ws = new WebSocket('ws://119.9.93.186:5490');
	//ws = new WebSocket('ws://m.3x.com.tw:5490');	
	//ws = new WebSocket('ws://119.9.24.48:8080');
	/*
	if(Math.random()<0.5){
		ws = new WebSocket('ws://119.9.24.48:5490');	
	} else {
		ws = new WebSocket('ws://119.9.40.105:5490');
	}*/
	//ws = new WebSocket('ws://119.9.40.105:5490');
	ws = new WebSocket('ws://119.9.24.48:5490');	
	/*
	if(typeof websocketip !="undefined" && websocketip>''){
		ws = new WebSocket('ws://'+websocketip+':5490');
	} else {
		ws = new WebSocket('ws://m.3x.com.tw:5490');
		//ws = new WebSocket('ws://120.132.85.234:5490');
		//ws = new WebSocket('ws://125.208.11.242:5490');
	}*/
	ws.onopen = function() {
		//console.log('open');
		//ws.send('Hello')  // Sends a message.
		err_cnt=0;
		getLast();
	}
	ws.onclose = function() {
		if(err_cnt++>0){
			alert("网路不稳定！若无法改善，请按F5刷新");
		}
		StartWS();
		//timeoutId = setTimeout("StartWS()",2000);

		/*
		if(confirm("disconnect!! Do you want to re-connect?")){
			StartWS();
		}*/
		
	}
	ws.onmessage = function(e) {
		// Receives a message.
		//console.log('message', e.data);	
		onDataWS(e);
	}
}
var LoginClass = new LoginClass(""); 
var prod_m="";
function LoginClass(FutureProxyURL){
	var lci=this;
	lci.se;	
	lci.getCount=3;
	lci.dailyCount=0;	
	lci.pickupData=new Array();
	lci.pickupDataSize=40;
	lci.getLast = function(e) {
		StartWS();
	}
}
function onDataWS(e){
	var data=JSON.parse(e.data);
	//console.log('message', data);
	if(data.t==Type_GetLast){
		//console.log(data.d);
		//console.log(data);
		LastPrice=data.d;
		PriceDot=data.pd;
		DotLength=PriceDot;
		prod_m=data.idm;


		if(prod.indexOf("IF300")>=0 || prod.indexOf("S2SFC")>=0){
			DotLength=1;
		}else if(prod.indexOf("WTX")>=0){DotLength=0;}
		if(country.indexOf("_SECOND")<0){
			if(typeof data.ot=="undefined" )openTime=opentime[country];//|| prod=="B1YM"
			else openTime=data.ot;
			if(typeof data.ct=="undefined" )closeTime=closetime[country];//|| prod=="B1YM"
			else closeTime=data.ct;		
		}else {
			openTime=opentime[country];
			closeTime=closetime[country];
			
		}
		openTimeGraph=opentimeGraph[country];
		closeTimeGraph=closetimeGraph[country];

		
	}else if(data.t==Type_GetDaily){


		var dailyArr=data.d.split("|");
		//nowPprice=dailyArr[1];
		//nowTqty=dailyArr[2];
		//alert(dailyArr[1])
		ClosePBar=parseInt(dailyArr[1]);
		OpenPBar=parseInt(dailyArr[3]);
		MaxPBar=parseInt(dailyArr[4]);
		MinPBar=parseInt(dailyArr[5]);
	}else if(data.t==Type_GetMinAllData){
		//console.log('prod',data.d);
		if(prod_m=="")prod_m=prod
		pushStockAll(data.d);
	}else if(data.t==Type_GetPic200){
		if(prod_m=="")prod_m=prod
		var data200=data.d;	
		//var PriceDot=data.pd;	
		if(data200!=""){
			var ara=data200.split(", ");
			for(var i=0;i<ara.length;i++){
				LoginClass.pickupData.push(ara[i])
			}
			//showDetailList(LoginClass.pickupData);
			var size = Object.size(LoginClass.pickupData);
			if(size>LoginClass.pickupDataSize)LoginClass.pickupData= LoginClass.pickupData.slice(size-LoginClass.pickupDataSize,size);
			showDetailList(LoginClass.pickupData);
			//console.log(LoginClass.pickupData.length);
			//console.log(LoginClass.pickupData[LoginClass.pickupData.length-2]);
			pushStockS(prod_m,LoginClass.pickupData[LoginClass.pickupData.length-2],"s");
		}
		
	}else if(data.t==Type_GetIndex){
		if(data.d!= "undefined"){
			var IndexInfo=data.d.trim();
			setIndexInfo(IndexInfo);
			//alert(IndexInfo)
		}
	}else if(data.t==Type_GetMinNowData){
		//console.log('prod',prod);
		//console.log('prod',data.d);
		pushStockM(prod,data.d,"m");
	}else if(data.t==Type_GetNow){
		//console.log(prod,data.d);
		if(prod_m=="")prod_m=prod

		var nowInfo=data.d;
		pushStockS(prod_m,nowInfo,"s");
		if(LoginClass.pickupData[LoginClass.pickupData.length-1]==nowInfo){							
		}else{
			LoginClass.pickupData.push(nowInfo)	;
		}
//console.log('nowInfo', nowInfo);	
		//console.log('nowInfo', nowInfo);	
		//console.log('LoginClass', LoginClass.pickupData.length);	
		var size = Object.size(LoginClass.pickupData);
		//console.log('size', size);	
		//console.log('size', LoginClass.pickupDataSize);	
		if(size>LoginClass.pickupDataSize)LoginClass.pickupData= LoginClass.pickupData.slice(size-LoginClass.pickupDataSize,size);
		showDetailList(LoginClass.pickupData);
		
	}else if(data.t==Type_Clear){
		//console.log('Type_Clear', e.data);	
		//console.log('d',dara.d.trim());	
		//console.log('di',dara.di.trim());	


		var d=data.d.trim();
		var di=data.di.trim();
		if(di==prod){		
			ClosePBar=0;
			OpenPBar=0;
			MaxPBar=0;
			MinPBar=9999999;
			//getLast();

			var d = new Date();
			//minDate=d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate();
			var hh=d.getHours();
			var mm=d.getMinutes();
			var ss=d.getSeconds();
			if(hh<10)hh="0"+hh;
			if(mm<10)mm="0"+mm;
			if(ss<10)ss="0"+ss;
			ch_country(hh+":"+mm+":"+ss)
			LoginClass.pickupData=new Array();
			showDetailList(LoginClass.pickupData);
			getLast();
		
		}
	}else if(data.t==Type_ModifyData){
		//console.log('Type_ModifyData', e.data);	
		var s=parseInt((Math.random()+0.5)*10000);
		setTimeout(function(){			
			ws.send('{"t":"'+Type_GetDaily+'","p":"'+prod+'"}');
			ws.send('{"t":"'+Type_GetMinAllData+'","p":"'+prod+'"}');
		
		},s);

		
		
	}
}












































function pushStockS(prod,data,type){
	var dataProd=financeData["mins"];
	var quote=financeData["quote"];
	if(dataProd.length>0 && dataProd[dataProd.length-1]["src"]==data){
	}else if(data>'' && data.indexOf("|")>0){
		//alert(data)
		var minDataArr=data.split("|");
		minDataArr[1]=minDataArr[1].trim();
		var minDate=minDataArr[1];
		var minTime=minDate;
		if(dataProd.length>0 && dataProd[dataProd.length-1].type!="m")dataProd.pop();
//console.log("*******");
		


		if(minDate.indexOf(" ")>=0){
			var tmp =minDate.split(" ");
				minDate=tmp[0];
				minTime=tmp[1];
		}else{
			minTime=minDate;
			var d = new Date();
			//minDate=d.getFullYear()+"-"+(d.getMonth()+1)+"-"+d.getDate();
			var mm=d.getMonth()+1;
			var dd=d.getDate();
			if(mm<10)mm="0"+mm;
			if(dd<10)dd="0"+dd;

			minDate=mm+"-"+dd;
		}
		
		//console.log(type);
		if(type=="s"){
			////2012-10-26 10:30:25|37375|21726
			//prod_id + "|" + prod_time_info + "|" + ara[2] + "|" + ara[3] + "|" + ara[4] + "|" + ara[5] + "|";
			//prod_id + "|" + prod_time_info + "|" + h + "|" + l + "|" + c + "|" + v + "|";

			

			
			if(country.indexOf("S2SFC")>=0){
				//console.log(minTime>=opentime["S2SFC_SECOND"]);
				//console.log(minTime,opentime["S2SFC_SECOND"]);
				if(minTime>=opentime["S2SFC_SECOND"]){
					minDate="3"+minTime;
					minTime=minTime;
				}		
			}else{
				minDate=minTime;
				if(minTime<opentime){
					minDate="3"+minTime;
				}
			}
			//console.log(minDate);
			
			/*
			var dateTimeAra=minDate.split(" ");
			if(dateTimeAra.length<2)dateTimeAra=minDate;
			minDate="3"+dateTimeAra[1];
			*/
		}
		//console.log(minDate,minTime);
		if(country=="S2SFC_SECOND"){
			if(minTime<opentime.S2SFC_SECOND)return;
		}
		
//console.log(minDate,dataProd[dataProd.length-1]["date"]);
		if(dataProd.length>0 &&  minDate<=dataProd[dataProd.length-1]["date"]){
			return;
		}
		/*
		var minTime=minDate;
		if(minTime.indexOf("3")==0){						
			minTime=minTime.substring(1,minTime.length);
		}
*/
		var tmpData=new Object();
			////2012-10-26 10:30:25|37375|21726
			//console.log((dataProd.length>0));

		
		if(dataProd.length>0){
			var oldData=dataProd[dataProd.length-1];
		} else {
			return !ch_country(quote["time"]);
		}

//console.log(minDate+","+minTime);
		var tmpqty=minDataArr[5]-oldData.qty_t;
		if(country.indexOf("_SECOND")>=0 && tmpqty<0)tmpqty=minDataArr[5];
		if(tmpqty>minDataQty){
			tmpqty=0;
		}
		if(tmpqty<=0)return;
		tmpData["prod"]=prod;
		tmpData["date"]=minDate;
		tmpData["time"]=minTime;
		tmpData["open"]=oldData.close;
		tmpData["high"]=minDataArr[2];
		tmpData["low"]=minDataArr[3];
		tmpData["close"]=minDataArr[4];
		tmpData["price"]=minDataArr[4];
		tmpData["qty_t"]=minDataArr[5];
		tmpData["qty"]=tmpqty;
		tmpData["volume"]=tmpqty;
		tmpData["amount"]=tmpqty;
		tmpData["src"]=data;
		tmpData["quoteTime"]=minTime;
		tmpData["preClose"]=minDataArr[4];
		tmpData["type"]=type;		
		
		dataProd.push(tmpData);
		ClosePBar=minDataArr[4];
		if(!isNaN(tmpData["high"])){
			MaxP=Math.max(MaxP,tmpData["high"]);
			MaxPBar=Math.max(MaxPBar,tmpData["high"]);			
		}
		if(!isNaN(tmpData["low"])){
			MinP=Math.min(MinP,tmpData["low"]);
			MinPBar=Math.min(MinPBar,tmpData["low"]);
		}
		if(OpenPBar==0)OpenPBar=tmpData["close"];

		quote["prod"]=prod;
		quote["time"]=dataProd[dataProd.length-1]["time"];
		quote["open"]=dataProd[0]["price"];
		quote["preClose"]=LastPrice;
		quote["highest"]=MaxP;
		quote["lowest"]=MinP;
		quote["price"]=dataProd[dataProd.length-1]["price"];
		quote["volume"]=dataProd[dataProd.length-1]["volume"];
		quote["amount"]=dataProd[dataProd.length-1]["amount"];

		//financeData["mins"]=dataProd;

		financeData["quote"]=quote;
		financeData["mins"]=dataProd;
		chart.paint(financeData);
		setBarData(financeData);
		return !ch_country(quote["time"]);
	}
}
function pushStockM(prod,data,type){
	//10:17:00|23000|23005|22997|23001|35249|387|
	//console.log("pushStockM",data)
	var dataProd=financeData["mins"];
	var quote=financeData["quote"];
	if(dataProd.length>0 && dataProd[dataProd.length-1]["src"]==data){
	}else if(data.indexOf("|")>0){
		//alert(data)
		var minDataArr=data.split("|");
		minDataArr[0]=minDataArr[0].trim();
		var minDate=minDataArr[0];
		if(dataProd.length>0 && dataProd[dataProd.length-1].type!="m")dataProd.pop();		
		if(dataProd.length>0 &&  minDate<=dataProd[dataProd.length-1]["date"]){
			return;
		}
		var minTime=minDate;
		if(minTime.indexOf("3")==0){						
			minTime=minTime.substring(1,minTime.length);
		}
		if(country=="S2SFC_SECOND"){
			if(minTime<opentime.S2SFC_SECOND)return;
		}

		var tmpData=new Object();
		if(country.indexOf("_SECOND")>=0 && minDataArr[6]<0)minDataArr[6]=minDataArr[5];
		if(minDataArr[6]>minDataQty)minDataArr[6]=0;
		if(minDataArr[6]<=0)return;
		tmpData["prod"]=prod;
		tmpData["date"]=minDate;
		tmpData["time"]=minTime;
		tmpData["open"]=minDataArr[1];
		tmpData["high"]=minDataArr[2];
		tmpData["low"]=minDataArr[3];
		tmpData["close"]=minDataArr[4];
		tmpData["price"]=minDataArr[4];
		tmpData["qty_t"]=minDataArr[5];
		tmpData["qty"]=minDataArr[6];
		tmpData["volume"]=minDataArr[6];
		tmpData["amount"]=minDataArr[6];		
		tmpData["src"]=data;
		tmpData["quoteTime"]=minTime;
		tmpData["preClose"]=minDataArr[4];
		tmpData["type"]=type;
		
		ClosePBar=parseInt(tmpData["close"]);
		
		dataProd.push(tmpData);

		//if(!isNaN(tmpData["high"]))MaxP=Math.max(MaxP,tmpData["high"]);
		//if(!isNaN(tmpData["low"]))MinP=Math.min(MinP,tmpData["low"]);

		if(!isNaN(tmpData["high"])){
			MaxP=Math.max(MaxP,tmpData["high"]);
			MaxPBar=Math.max(MaxPBar,tmpData["high"]);			
		}
		if(!isNaN(tmpData["low"])){
			MinP=Math.min(MinP,tmpData["low"]);
			MinPBar=Math.min(MinPBar,tmpData["low"]);
		}


		quote["prod"]=prod_m;
		quote["time"]=dataProd[dataProd.length-1]["time"];
		quote["open"]=dataProd[0]["price"];
		quote["preClose"]=LastPrice;
		quote["highest"]=MaxP;
		quote["lowest"]=MinP;
		quote["price"]=dataProd[dataProd.length-1]["price"];
		quote["volume"]=dataProd[dataProd.length-1]["volume"];
		quote["amount"]=dataProd[dataProd.length-1]["amount"];

		//financeData["mins"]=dataProd;

		financeData["quote"]=quote;
		financeData["mins"]=dataProd;
		chart.paint(financeData);
		setBarData(financeData);


		return !ch_country(quote["time"]);
	
	}
}
function pushStockAll(data){
//console.log("pushStockAll",data)
	//console.log("country",country)
	
	var dataProd=new Array();	
	if(data.indexOf("@")>0){
		
		var arrMouse=data.split("@");
		var prod=arrMouse[2];

		if(arrMouse[3].indexOf(",")>0){
			var arr=arrMouse[3].split(",");
			//if(arr.length>dataLengthhArray[prod])
			//alert(arr.length)
			for(var i=0;i<arr.length;i++){		
				if(arr[i].indexOf("|")>0){
					var minDataArr=arr[i].split("|");
					var tmpData=new Object();
					minDataArr[0]=minDataArr[0].trim();
					var minDate=minDataArr[0];
					//console.log("minDate",minDate)
					var minTime=minDate;
					if(minTime.indexOf("3")==0){						
						minTime=minTime.substring(1,minTime.length);
					}
					if(country=="S2SFC_SECOND"){
				
					}else if(dataProd.length>0 && minDate<=dataProd[dataProd.length-1]["date"]){
						continue;
					}
					


					
					if(country.indexOf("_SECOND")>=0 && minDataArr[6]<0)minDataArr[6]=minDataArr[5];
					if(minDataArr[6]>minDataQty)minDataArr[6]=0;
					if(minDataArr[6]<=0)continue;
//console.log("minTime",minTime)
					if(country=="S2SFC_SECOND"){
						if(minTime<opentime.S2SFC_SECOND || minTime>closetime.S2SFC_SECOND)continue;
					}
					//console.log("minTime",minTime)

//console.log(minDate+","+minTime);
					tmpData["prod"]=prod;
					tmpData["date"]=minDate;
					tmpData["time"]=minTime;					
					tmpData["open"]=minDataArr[1];
					tmpData["high"]=minDataArr[2];
					tmpData["low"]=minDataArr[3];
					tmpData["close"]=minDataArr[4];
					tmpData["price"]=minDataArr[4];
					tmpData["qty_t"]=minDataArr[5];
					tmpData["qty"]=minDataArr[6];
					tmpData["volume"]=minDataArr[6];
					tmpData["amount"]=minDataArr[6];
					tmpData["src"]=arr[i].trim();
					tmpData["quoteTime"]=minTime;
					tmpData["preClose"]=minDataArr[4];
					tmpData["type"]="m";
					dataProd.push(tmpData);
					
					if(!isNaN(tmpData["high"]))MaxP=Math.max(MaxP,tmpData["high"]);
					if(!isNaN(tmpData["low"]))MinP=Math.min(MinP,tmpData["low"]);
				
				}				
			}
		}		
	}

	

	//alert(dataProd[dataProd.length-1]["time"])
	if(dataProd.length>0){
		var quote=new Object();
		quote["prod"]=prod;
		quote["time"]=dataProd[dataProd.length-1]["time"];
		quote["open"]=dataProd[0]["price"];
		quote["preClose"]=LastPrice;
		quote["highest"]=MaxP;
		quote["lowest"]=MinP;
		quote["price"]=dataProd[dataProd.length-1]["price"];
		quote["volume"]=dataProd[dataProd.length-1]["volume"];
		quote["amount"]=dataProd[dataProd.length-1]["amount"];

		financeData["quote"]=quote;
		financeData["mins"]=dataProd;
		chart.paint(financeData);
		setBarData(financeData);

//console.log(financeData);
		return !ch_country(quote["time"]);
	}else{
		var quote=new Object();
		quote["prod"]=prod;
		quote["preClose"]=LastPrice;
		financeData["quote"]=quote;
		financeData["mins"]=dataProd;
		chart.paintSpace(financeData);		
		//return false;
	}
	//console.log(financeData);
	return true;
}
function ch_country(time){
	var rb=false;
	//alert("country="+country)
	if (prod.indexOf("HSCE") >= 0 || prod.indexOf("HSI") >= 0 ){
		var timeF="09:00:00";				
		var timeS="16:00:00";		
		
		if(time>=timeS && country.indexOf("_SECOND") < 0){
			country=prod+"_SECOND";
			localStorage.SelCountry=country;

			dataLength=dataLengthhArray[country];
			rateW=painWidth/defultpainWidth*(defultpainWidth/dataLength);
			chart = new minsChart('canvas',ChartArray[country]);
			//alert(country)
			//LoginClass.getLast();
			//getLast();
			rb=true;
		}else if(time>=timeF && time<timeS && country.indexOf("_SECOND") >= 0){
			country=country.substring(0,country.indexOf("_SECOND"));
			localStorage.SelCountry=country;
			dataLength=dataLengthhArray[country];
			rateW=painWidth/defultpainWidth*(defultpainWidth/dataLength);
			chart = new minsChart('canvas',ChartArray[country]);
			//alert(country)
			//LoginClass.getLast();
			//getLast();
			rb=true;
		}	
	}else if(prod.indexOf("S2SFC") >= 0){
		
		var timeF="16:30:00";				
		var timeS="02:00:00";		
		/*
		console.log("******");
		console.log(time);
		console.log((time>=timeS && time<timeF));*/
		if((time>="08:59:00" && time<timeF) && country.indexOf("_SECOND") < 0){
			country=prod+"_SECOND";
			localStorage.SelCountry=country;

			dataLength=dataLengthhArray[country];
			rateW=painWidth/defultpainWidth*(defultpainWidth/dataLength);
			chart = new minsChart('canvas',ChartArray[country]);

			
			if(typeof financeData !="undefined"){
				var dataProd=financeData["mins"];	
				//console.log(financeData);
				if(typeof dataProd!="undefined"){
					var Ndata=new Array();
					for(var i=0;i<dataProd.length;i++){
						if(dataProd[i].time>="08:59:00" && dataProd[i].time<timeF){
							Ndata.push(dataProd[i]);
						}
					}
					financeData["mins"]=Ndata;
					chart.paintSpace(financeData);					
				}
			}
			
			
				
/*
			financeData=new Object();
			var dataProd=new Array();	
			var quote=new Object();
			financeData["quote"]=quote;
			financeData["mins"]=dataProd;
			chart.paintSpace(financeData);		
			getAllM();*/
			rb=true;
		}else if((time<=timeS || time>timeF) && country.indexOf("_SECOND") >= 0){
			country=country.substring(0,country.indexOf("_SECOND"));
			localStorage.SelCountry=country;
			
			dataLength=dataLengthhArray[country];
			rateW=painWidth/defultpainWidth*(defultpainWidth/dataLength);
			chart = new minsChart('canvas',ChartArray[country]);


			if(typeof financeData !="undefined"){

			}
			//financeData=new Object();
			var dataProd=new Array();	
			var quote=new Object();
			financeData["quote"]=quote;
			financeData["mins"]=dataProd;


			//chart.paintSpace(financeData);		
			//alert(country)
			/*
			financeData=new Object();
			var dataProd=new Array();	
			var quote=new Object();
			financeData["quote"]=quote;
			financeData["mins"]=dataProd;
			chart.paintSpace(financeData);		
			getAllM();*/
			rb=true;
		}	
	}else{
		country=prod;
		localStorage.SelCountry=country;
	}
	return rb;
}
function chProd(str,bl){//,bl=false



	bl = typeof bl !== 'undefined' ? bl : false;
	if((typeof str !='undefined' && str!=prod) || bl==true){	
		//$("#PD_NAME").html("产品名称："+getProdNameMonth(quote["prod"]));
		
		$("#PD_NO").html("产品代号："+str);
		$("#PD_NAME").html("产品名称："+getProdName(str));

		prod=str;
		localStorage.SelProd=prod;

		country=prod;
		localStorage.SelCountry=country;


		dataLength=dataLengthhArray[country];
		rateW=painWidth/defultpainWidth*(defultpainWidth/dataLength);
		chart = new minsChart('canvas',ChartArray[country]);
		//alert(country)
		LoginClass.pickupData=new Array();		
		showDetailList(LoginClass.pickupData);
		//LoginClass.getLast();
		getLast();

	}
	
	$('#EDIT_CLOSE').click();
	return false;
}
function isOverDate(){
	if(openTime>closeTime)return true;
	return false;
}
function isOverTime(nowTime){
	if(this.isOverDate()){
		if(nowTime<=closeTime)return true;
	}
	return false;		
}
function setBarData(financeData){
	var dataProd=financeData["mins"];
	var data=dataProd[dataProd.length-1];
	var quote=financeData["quote"];
	
	var price=(ClosePBar==0)?data["close"]:ClosePBar;
	var diff = toMoney(price - LastPrice,0);
	//alert(price)

	var isRise = parseInt(price) > parseInt(LastPrice);
	var isEqual = parseInt(price) == parseInt(LastPrice);
	var isFall = parseInt(price) < parseInt(LastPrice);
	var txtRiseFall =  toMoney(diff * 100 / LastPrice,2) + '%';


	var isRiseH = parseInt(MaxPBar) > parseInt(LastPrice);
	var isEqualH = parseInt(MaxPBar) == parseInt(LastPrice);
	var isFallH = parseInt(MaxPBar) < parseInt(LastPrice);

	var isRiseL = parseInt(MinPBar) > parseInt(LastPrice);
	var isEqualL = parseInt(MinPBar) == parseInt(LastPrice);
	var isFallL = parseInt(MinPBar) < parseInt(LastPrice);

	var isRiseO = parseInt(OpenPBar) > parseInt(LastPrice);
	var isEqualO = parseInt(OpenPBar) == parseInt(LastPrice);
	var isFallO = parseInt(OpenPBar) < parseInt(LastPrice);
	
	var riseColor='red';
	var fallColor='green';
	var normalColor='black';

	var Style = isRise ? riseColor : (isFall ? fallColor : normalColor);
	var StyleH = isRiseH ? riseColor : (isFallH ? fallColor : normalColor);
	var StyleL = isRiseL ? riseColor : (isFallL ? fallColor : normalColor);
	var StyleO = isRiseO ? riseColor : (isFallO ? fallColor : normalColor);

	
	
//console.log("setBarData "+price+","+PriceDot+","+DotLength);
	$('#barPrice').html(toMoney(price/Math.pow(10,PriceDot),DotLength));	
	$('#barDiff').html(toMoney(diff/Math.pow(10,PriceDot),DotLength));
	$('#barHeigh').html(toMoney(MaxPBar/Math.pow(10,PriceDot),DotLength));
	$('#barLow').html(toMoney(MinPBar/Math.pow(10,PriceDot),DotLength));
	//$('#barVol').html(toMoney(data["qty_t"]/Math.pow(10,PriceDot),DotLength));
	$('#barVol').html(toMoney(data["qty_t"],0));
	$('#barPercent').html(txtRiseFall);


	$('#barOpen').html(toMoney(OpenPBar/Math.pow(10,PriceDot),DotLength));
	$('#barCloseY').html(toMoney(LastPrice/Math.pow(10,PriceDot),DotLength));


	$('#barPrice').css('color',Style);
	$('#barDiff').css('color',Style);	
	$('#barPercent').css('color',Style);

	$('#barHeigh').css('color',StyleH);
	$('#barLow').css('color',StyleL);

	$('#barOpen').css('color',StyleO);
	$('#barCloseY').css('color',normalColor);
//console.log(data);
/*
	setTopBarProd(prodindex[data["prod"]]);
	setTopBarTime(data["time"]);
	setTopBarPrice(toMoney(price/Math.pow(10,PriceDot),DotLength));
	setTopBarChange(toMoney(diff/Math.pow(10,PriceDot),DotLength));
	setTopBarPerChange(txtRiseFall);
	//console.log(data);
*/	
	if(price==0){
	/*
		setTopBarPrice("--");
		setTopBarChange("--");
		setTopBarPerChange("--");*/
		$('#barPrice').html("--");	
		$('#barDiff').html("--");
		$('#barPercent').html("--");

		$('#barPrice').css('color',normalColor);
		$('#barDiff').css('color',normalColor);	
		$('#barPercent').css('color',normalColor);	
	}
	if(OpenPBar==0){
		$('#barOpen').html("--");
		$('#barOpen').css('color',normalColor);
	}
	if(MaxPBar==0){
		$('#barHeigh').html("--");
		$('#barHeigh').css('color',normalColor);
	}
	if(MinPBar==99999999){
		$('#barLow').html("--");
		$('#barLow').css('color',normalColor);
	}
}
function setIndexInfo(src){	
	if(typeof src !="undefined"){
		var arr=src.split("@");
		for(var i=0;i<arr.length;i++){
			if(typeof arr[i] =="undefined" || arr[i].trim()=="")continue;
			var obj=arr[i].split("|");
			//NKI,KOR,HSI,HSC,SHI,SHSZ300,DJI,NAS,YDX,FTE,CAC,FTH,DAX
			var no=obj[0];
			var now=(obj[1]=="--")?obj[1]:parseInt(obj[1]);
			var close=(obj[2]=="--")?obj[2]:parseInt(obj[2]);
			var heigh=(obj[3]=="--")?obj[3]:parseInt(obj[3]);
			var low=(obj[4]=="--")?obj[4]:parseInt(obj[4]);
			var Change=(now=="--" || close=="--")?"--":(now-close);
			var Percent=(Change=="--" || close=="--")?"--":(Change/close*100);

			if(low=="99999999"){
				low="--";
			}
			if(heigh=="0"){
				heigh="--";
			}

			var now_o=formatPrice(no, now);
			var close_o=formatPrice(no, close);
			var heigh_o=formatPrice(no, heigh);
			var low_o=formatPrice(no, low);		
			Change=parseInt(now_o.price*100-close_o.price*100)/100;

			if($('#'+no+'_now').html()==now_o.price){				
				$('#'+no+'_now_td').attr("class","DATAINP_SPACE");
				$('#'+no+'_now').attr("class","TAB_BOX_DATA_W");
				//$('#'+no+'_now').css("background-color","#FFFFFF");
			}else {
				$('#'+no+'_now_td').attr("class","DATAINP_BK");
				if($('#'+no+'_now').html()=="--") $('#'+no+'_now').attr("class","TAB_BOX_DATA_W");
				else if(now_o.price>$('#'+no+'_now').html())$('#'+no+'_now').attr("class","TAB_BOX_DATA_R");
				else if(now_o.price<$('#'+no+'_now').html())$('#'+no+'_now').attr("class","TAB_BOX_DATA_G");
				else $('#'+no+'_now').attr("class","");
				//$('#'+no+'_now').css("background-color","");				
			}
			if($('#'+no+'_close').html()==close_o.price){
				$('#'+no+'_close_td').attr("class","DATAINP_SPACE");
				$('#'+no+'_close').attr("class","TAB_BOX_DATA_W");
				//$('#'+no+'_close').css("background-color","#FFFFFF");
			}else {
				$('#'+no+'_close_td').attr("class","DATAINP_BK");
				if($('#'+no+'_close').html()=="--") $('#'+no+'_close').attr("class","TAB_BOX_DATA_W");
				else if(close_o.price>$('#'+no+'_close').html())$('#'+no+'_close').attr("class","TAB_BOX_DATA_R");
				else if(close_o.price<$('#'+no+'_close').html())$('#'+no+'_close').attr("class","TAB_BOX_DATA_G");
				else $('#'+no+'_close').attr("class","");
				//$('#'+no+'_close').css("background-color","#CCCCCC");		
			}
			if($('#'+no+'_heigh').html()==heigh_o.price){
				$('#'+no+'_heigh_td').attr("class","DATAINP_SPACE");
				$('#'+no+'_heigh').attr("class","TAB_BOX_DATA_W");
				//$('#'+no+'_heigh').css("background-color","#FFFFFF");
			}else {
				$('#'+no+'_heigh_td').attr("class","DATAINP_BK");
				if($('#'+no+'_heigh').html()=="--") $('#'+no+'_heigh').attr("class","TAB_BOX_DATA_W");
				else if(heigh_o.price>$('#'+no+'_heigh').html())$('#'+no+'_heigh').attr("class","TAB_BOX_DATA_R");
				else if(heigh_o.price<$('#'+no+'_heigh').html())$('#'+no+'_heigh').attr("class","TAB_BOX_DATA_G");
				else $('#'+no+'_heigh').attr("class","");
				//$('#'+no+'_heigh').css("background-color","#CCCCCC");		
			}
			if($('#'+no+'_low').html()==low_o.price){
				$('#'+no+'_low_td').attr("class","DATAINP_SPACE");
				$('#'+no+'_low').attr("class","TAB_BOX_DATA_W");
				//$('#'+no+'_low').css("background-color","#FFFFFF");
			}else {
				$('#'+no+'_low_td').attr("class","DATAINP_BK");
				if($('#'+no+'_low').html()=="--") $('#'+no+'_low').attr("class","TAB_BOX_DATA_W");
				else if(low_o.price>$('#'+no+'_low').html())$('#'+no+'_low').attr("class","TAB_BOX_DATA_R");
				else if(low_o.price<$('#'+no+'_low').html())$('#'+no+'_low').attr("class","TAB_BOX_DATA_G");
				else $('#'+no+'_low').attr("class","");
				//$('#'+no+'_low').css("background-color","#CCCCCC");		
			}
			if($('#'+no+'_Change').html()==Change){
				$('#'+no+'_Change_td').attr("class","DATAINP_SPACE");
				$('#'+no+'_Change').attr("class","TAB_BOX_DATA_W");
				//$('#'+no+'_Change').css("background-color","#FFFFFF");
			}else {
				$('#'+no+'_Change_td').attr("class","DATAINP_BK");
				$('#'+no+'_Change').attr("class","TAB_BOX_DATA_W");
			}
			if($('#'+no+'_Percent').html()==(toMoney(Percent)+"%")){
				$('#'+no+'_Percent_td').attr("class","DATAINP_SPACE");
				$('#'+no+'_Percent').attr("class","TAB_BOX_DATA_W");
			}else {
				$('#'+no+'_Percent_td').attr("class","DATAINP_BK");
				$('#'+no+'_Percent').attr("class","TAB_BOX_DATA_W");
				
			}


			var indexNow=now_o.price.substring(0,7);
			if(now_o.price<1000)indexNow=now_o.price.substring(0,5);
			else if(now_o.price<10000)indexNow=now_o.price.substring(0,6);


			var indexClose=close_o.price.substring(0,7);
			if(close_o.price<1000)indexClose=close_o.price.substring(0,5);
			else if(close_o.price<10000)indexClose=close_o.price.substring(0,6);

			var indexHeigh=heigh_o.price.substring(0,7);
			if(heigh_o.price<1000)indexHeigh=heigh_o.price.substring(0,5);
			else if(heigh_o.price<10000)indexHeigh=heigh_o.price.substring(0,6);

			var indexLow=low_o.price.substring(0,7);
			if(low_o.price<1000)indexLow=low_o.price.substring(0,5);
			else if(low_o.price<10000)indexLow=low_o.price.substring(0,6);


			$('#'+no+'_now').html(indexNow);			
			$('#'+no+'_close').html(indexClose);
			$('#'+no+'_heigh').html(indexHeigh);
			$('#'+no+'_low').html(indexLow);
			$('#'+no+'_Change').html(Change);
			$('#'+no+'_Percent').html(toMoney(Percent)+"");//%


			setIndexInfoColor("#"+no+"_close","--","--");
			setIndexInfoColor("#"+no+"_now",now,close);
			setIndexInfoColor("#"+no+"_heigh",heigh,close);
			setIndexInfoColor("#"+no+"_low",low,close);
			setIndexInfoColor("#"+no+"_Change",now,close);
			setIndexInfoColor("#"+no+"_Percent",now,close);
		}
	}
}
function setIndexInfoColor(idStr,p,close){	
	if(p=="--" || close=="--"){
		$(idStr).css("color", "#000000");
		return;
	}
	if(p>close)$(idStr).css("color", "#F00");
	else if(p<close)$(idStr).css("color", "#0d9e0d");
	else $(idStr).css("color", "#000000");
}
function formatPrice(id, price)	{
	var o=new Object();
	if(price=="--"){
		o.price=price;
		o.float=price;
		return o;
	}
	var priceStr=price+"";
	var f=parseInt(priceStr.substr(0, 1))
	var format=1;
	var d=-1
	switch (id){
		case "NKI":
			d=(f < 5) ? 5 : 4
			break;
		case "KOR":
			d=(f < 5) ? 4 : 3
			break;
		case "HSI":
			d=(f < 5) ? 5 : 4
			break;
		case "SZI":
			d=(f < 5) ? 4 : 4
			break;
		case "SHI":
			d=(f < 5) ? 4 : 4
			break;
		case "SHSZ300":
			d=(f < 5) ? 4 : 4
			break;
		case "SFCI":
			d=(f < 5) ? 5 : 4
			break;
		case "DJI":
			d=(f < 5) ? 5 : 4
			break;
		case "NAS":
			d=(f < 5) ? 4 : 4
			break;
		case "YDX":
			d=(f < 5) ? 3 : 2
			break;
		case "SOX":
			d=(f < 5) ? 3 : 3
			break;
		case "FTE":
			d=(f < 5) ? 3 : 3
			break;
		case "CAC":
			d=(f < 5) ? 4 : 4
			break;
		case "FTH":
			d=(f < 5) ? 4 : 4
			break;
		case "DAX":
			d=(f < 5) ? 5 : 4
			break;
		case "HSC":
			d=(f < 5) ? 5 : 4
			break;
		case "SP5":
			d=(f < 5) ? 4 : 3
			break;
	}
	
	
	if (d < 0){
		o.price=(price / format)+"";
		var index=o.price.indexOf(".") + 1;
		o.float=(index <= 0) ? 1 : Math.pow(10, o.price.length - index);		
	}else{
		var decimal=priceStr.substr(d);
		o.price=priceStr.substr(0, d) + "." + decimal;
		o.float=Math.pow(10, decimal.length);
	}
	return o;
}




























 function line(ctx, x0, y0, x1, y1, color, width) {
	ctx.beginPath();
	ctx.moveTo(x0, y0);
	ctx.lineTo(x1, y1);
	ctx.strokeStyle = color;
	ctx.lineWidth = width || 1;
	ctx.stroke();
}

function getMinTime(minIndex) {
	//上午09：30-11：30
	//下午13：00-15：00
	var d = new Date();
	if (minIndex <= 180) {
		d.setHours(9, 0, 0);
		d = new Date(d.getTime() + (minIndex) * 60 * 1000);
	} else {
		d.setHours(13, 0, 0);
		d = new Date(d.getTime() + (minIndex - 180) * 60 * 1000);
	}


	var hour = d.getHours() > 9 ? new String(d.getHours()) : '0' + d.getHours();
	var minutes = d.getMinutes() > 9 ? new String(d.getMinutes()) : '0' + d.getMinutes();
	var seconds = '';
	return hour + '' + minutes + seconds;
}

function Tip(options) {
	this.options = options;
	this.canvas = options.canvas;
	this.canvas.tip = this;
}

Tip.prototype = {
	show: function (relativePoint, html) {
		var dc = this.dataContext;
		var painter = this.canvas.painter;
		if (dc) {

			if (dc.isNewQuote) painter.fillTopText(dc.data);
			else painter.fillTopText(dc.data, dc.index);
			
		}
	},
	update: function (relativePoint, html) {
		this.show(relativePoint, html);
	},
	hide: function () {
		var dc = this.dataContext;
		var painter = this.canvas.painter;
		if (dc) {
			painter.fillTopText(dc.data);
			
		}
	}
};

function minsChart(canvasId, options) {
	extendObject(options, this);
	this.canvas = $id(canvasId);
	this.ctx = this.canvas.getContext('2d');
	this.canvas.painter = this;
	this.rateW=rateW;
	this.prod=prod;
	this.isKL=false;
	this.orderPrice={}
}

minsChart.prototype = {
	/*
	data format like :{
	quote: {
	time: 20111214150106,
	open: 2241.390,
	preClose: 2248.590,
	highest: 2256.740,
	lowest: 2224.730,
	price: 2228.530,
	volume: 4407982200,
	amount: 38621178573
	},
	mins: [
	{price:2239.45,volume:49499299,amount:459279327}
	]
	}
	*/	
	setOrderPrice: function (ara){
		this.orderPrice=ara;
	},
	paint: function (data,price, time) {
		//console.log("paint");
		if(typeof localStorage.isKL == 'undefined'){
			localStorage.isKL ="false";
		}
		if(localStorage.isKL == "true"){
			drawKL(localStorage.KLineMin);
		}else{
			this.openTime=openTime;
			this.closeTime=closeTime;

			this.openTimeGraph=openTimeGraph;
			this.closeTime=closeTime;
			this.closeTimeGraph=closeTimeGraph;


							
			
			var ctx = this.ctx;
			var options = this.volume;
			ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);		
			if (typeof price == 'undefined' || typeof time == 'undefined' ) this.fillTopText(data);

			else this.fillTopTextNow(financeData,price, time);
			this.paintChart(data);		
			this.paintxAxis();
			this.fillBottomText(data);
			this.paintVolume(data);
			//console.log(data);


		}		
	},
	paintSpace: function (data,price, time) {	
		this.openTime=openTime;
		this.closeTime=closeTime;

		this.openTimeGraph=openTimeGraph;
		this.closeTime=closeTime;
		this.closeTimeGraph=closeTimeGraph;

		
		var ctx = this.ctx;
		var options = this.volume;
		ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);		
		
		if (typeof price == 'undefined' || typeof time == 'undefined' ) this.fillTopText(data);
		else this.fillTopTextNow(financeData,"--", "--");
		this.paintChart(data);		
		this.paintxAxis();
		this.fillBottomText(data);
		
	},
	paintVolume: function (data) {
		var ctx = this.ctx;
		var options = this.volume;
		ctx.lineWidth=options.lineWidth;
		ctx.beginPath();
		ctx.rect(options.region.x, options.region.y, options.region.width, options.region.height);
		ctx.strokeStyle = options.borderColor;
		ctx.stroke();
		line(ctx, options.region.x, options.region.y + options.region.height / 4, options.region.x + options.region.width, options.region.y + options.region.height / 4, options.splitLineColor,options.lineWidth);
		line(ctx, options.region.x, options.region.y + options.region.height / 2, options.region.x + options.region.width, options.region.y + options.region.height / 2, options.splitLineColor,options.lineWidth);
		line(ctx, options.region.x, options.region.y + options.region.height*3 / 4, options.region.x + options.region.width, options.region.y + options.region.height*3 / 4, options.splitLineColor,options.lineWidth);
		options.getDataLength = function () { return this.data.items.length; };
		options.maxDotsCount = this.maxDotsCount;
		options.rateW = this.rateW;
		options.prod = this.prod;
		options.openTime = this.openTime;
		options.openTimeGraph = this.openTimeGraph;
		
		options.closeTime = this.closeTime;
		options.closeTimeGraph = this.closeTimeGraph;
		
		options.linedata = this.linedata;
		
		var volumePainterImp = new volumePainter(options,this.rateW);
		var painter = new Painter(this.canvas.id, volumePainterImp, { items: data.mins });
		painter.paint();

		var max = painter.maxVolume;
		var unit;
		/*
		if (max / 1000000 > 1000) {
			max = max / 1000000;
			unit = '百万';
		} else {
			max = max / 10000;
			unit = '万';
		}*/
		var tmpVUni=(max /4);
		//var scalers = [max, (3*tmpVUni).toFixed(0), (2*tmpVUni).toFixed(0),(tmpVUni).toFixed(0), '(Qty)'];
		var scalers = [max, (3*tmpVUni).toFixed(0), (2*tmpVUni).toFixed(0),(tmpVUni).toFixed(0), ''];
		var yscaler = new yAxis(this.volume.yScaler);
		var painter = new Painter(this.canvas.id, yscaler, scalers);
		painter.paint();
	},

	fillBottomText: function (data) {
		if (!this.bottomText) return;
		//高9999 低9999 成交888999
		var ctx = this.ctx;
		var txt = '高';
		var options = this.bottomText;
		ctx.font = options.font;
		ctx.fillStyle = options.color;
		var w = ctx.measureText(txt).width;
		ctx.fillText(txt, options.region.x, options.region.y);
		var x = options.region.x + w;
		var quote = data.quote;
		var me = this;
		function getTxtColor(val) { return parseInt(val) > parseInt(LastPrice) ? me.riseColor : (parseInt(val) == parseInt(LastPrice) ? me.normalColor : me.fallColor); }
		var highColor = getTxtColor(quote.highest);
		var high = toMoney(quote.highest/Math.pow(10,PriceDot),DotLength);//toMoney(quote.highest,0);
		ctx.fillStyle = highColor;
		w = ctx.measureText(high).width;
		ctx.fillText(high, x, options.region.y);
		x += w;
		txt = ' 低';
		ctx.fillStyle = options.color;
		w = ctx.measureText(txt).width;
		ctx.fillText(txt, x, options.region.y);
		x += w;
		var lowColor = getTxtColor(quote.lowest);
		var low = toMoney(quote.lowest/Math.pow(10,PriceDot),DotLength);//toMoney(quote.lowest,0);
		w = ctx.measureText(low).width;
		ctx.fillStyle = lowColor;
		ctx.fillText(low, x, options.region.y);
		x += w;
		ctx.fillStyle = options.color;
		var amount = ' 成交' + bigNumberToText(quote.amount);
		ctx.fillText(amount, x, options.region.y);
	},

	paintxAxis: function () {
		var xAxisImpl = new xAxis(this.xScaler,this.rateW);
		var xAxisPainter = new Painter(this.canvas.id, xAxisImpl, this.xScaler.data);

		
		xAxisPainter.paint();
	},

	paintChart: function (data) {
		var minsChartOptions = this.minsChart;
		var region = this.minsChart.region;
		var linedata = this.minsChart.linedata;
		var ctx = this.ctx;		
		ctx.lineWidth=minsChartOptions.lineWidth;
		ctx.beginPath();
		ctx.strokeStyle = minsChartOptions.borderColor;
		ctx.rect(region.x, region.y, region.width, region.height);
		ctx.stroke();

		//水平线
		var middleIndex = (this.minsChart.horizontalLineCount + this.minsChart.horizontalLineCount % 2) / 2;
		var splitCount = this.minsChart.horizontalLineCount + 1;
		for (var i = 1; i <= this.minsChart.horizontalLineCount; i++) {
			var color = minsChartOptions.otherSplitLineColor;
			var y = region.y + region.height * i / splitCount;
			line(ctx, region.x, y, region.x + region.width, y, color,minsChartOptions.lineWidth);
		}
		//垂直线 
		splitCount = this.minsChart.verticalLineCount ;
		var tX=0;
		for (var i = 0; i <= this.minsChart.verticalLineCount; i++) {
			//alert(linedata[i]+","+this.rateW)
			tX+=linedata[i]*this.rateW;
			var x =  region.x + tX //region.width/this.minsChart.verticalLineCount *i //region.width * i / splitCount;		//60*rateW*i			
			line(ctx, x, region.y, x, region.y + region.height, minsChartOptions.otherSplitLineColor,minsChartOptions.lineWidth);
		}
		ctx.lineWidth=minsChartOptions.priceLineWidth;
		//console.log("data.quote.preClose",data.quote.preClose);
		//价格线
		var lineOptions = {
			prod: this.prod,
			rateW: this.rateW,
			openTime: this.openTime,
			openTimeGraph: this.openTimeGraph,
				
			closeTime: this.closeTime,
			closeTimeGraph: this.closeTimeGraph,
				
			linedata:linedata,
			region: region,
			maxDotsCount: this.maxDotsCount,
			getDataLength: function () { return this.data.items.length; },
			getItemValue: function (item) { return item.price; },
			middleValue: data.quote.preClose, //通常是昨收
			lineColor: minsChartOptions.priceLineColor
		};
		var linePainterImp = new linePainter(lineOptions,this.rateW);
		var priceLinePainter = new Painter(this.canvas.id, linePainterImp, { items: data.mins,quote: data.quote });
		priceLinePainter.paint();

		//昨收
		var midcolor = minsChartOptions.middleLineColor;
		var middiff =Math.abs(data.quote.preClose - (Math.min(data.quote.lowest,data.quote.preClose)-20));
		var midY= region.y+( 1- middiff /  priceLinePainter.maxDiff )*region.height;		
		line(ctx, region.x, midY, region.x + region.width, midY, midcolor);

/*
		if(this.orderPrice.length>0){
			for(var odi=0;odi<this.orderPrice.length;odi++){
				var orderprice=this.orderPrice[odi];
				var ordermiddiff =Math.abs(orderprice - (Math.min(data.quote.lowest,data.quote.preClose)-20));
				var orderY= region.y+( 1- ordermiddiff /  priceLinePainter.maxDiff )*region.height;	
				line(ctx, region.x, orderY, region.x + region.width, orderY, "#33ffff");
				var txt = toMoney(orderprice/Math.pow(10,PriceDot),1);
				ctx.fillStyle = "#33ffff";		
				ctx.fillText(txt, region.x+10, orderY-5);
			}
		}*/

		//var Nprice=data.quote.price;
		if(data.mins.length<=00){
			return;
		}
		var Nprice=data.mins[data.mins.length-1].price;
		var Nmiddiff =Math.abs(Nprice - (Math.min(data.quote.lowest,data.quote.preClose)-20));
		var orderY= region.y+( 1- Nmiddiff /  priceLinePainter.maxDiff )*region.height;	

		//priceLinePainter

		var tmpXN=priceLinePainter.paintImplement.getX.call(priceLinePainter,data.mins.length-1)
		//var orderY= region.x+( 1- ordermiddiff /  priceLinePainter.maxDiff )*region.height;	
		//console.log(tmpXN)
		if(tmpXN>(region.width/2)){
			line(ctx, region.x, orderY, region.x + (tmpXN), orderY,  "#999900");
			var txtN = toMoney(Nprice/Math.pow(10,PriceDot),1);
			ctx.fillStyle = "#999900";		
			ctx.fillText(txtN, region.x+10, orderY-5);
		}else{
			line(ctx, region.x+(tmpXN), orderY, region.x + region.width, orderY,  "#999900");
			var txtN = toMoney(Nprice/Math.pow(10,PriceDot),1);
			ctx.fillStyle = "#999900";		
			ctx.fillText(txtN, region.x + region.width-40, orderY-5);
		}
		


		

		//y轴
		var yOptions = this.minsChart.yScalerLeft;
		var preClose = data.quote.preClose;
		var me = this;
		yOptions.color = function (val) {
			//return val > preClose ? me.riseColor : (val == preClose ? me.normalColor : me.fallColor);
			return me.normalColor ;
		};
		var scalersLeft = [];
		var scalersRight = [];
		//var min = preClose - priceLinePainter.maxDiff;
		//var space = priceLinePainter.maxDiff * 2 / (this.minsChart.horizontalLineCount + 1);
		var min =  Math.min(data.quote.lowest,data.quote.preClose)-20;
		var space = priceLinePainter.maxDiff / (this.minsChart.horizontalLineCount + 1);
		for (var i = this.minsChart.horizontalLineCount + 1; i >= 0; i--) {
			var val = min + i * space;
			if(this.prod=="N1CL"){
				var leftP=toMoney(val/Math.pow(10,PriceDot),2);
				if(isNaN(leftP))leftP="--";
				scalersLeft.push(leftP);//toMoney(val,0)

				/*
			}else if(this.prod=="M1EC") {
				var leftP=toMoney(val/Math.pow(10,PriceDot),2);
				if(isNaN(leftP))leftP="--";
				scalersLeft.push(leftP);//toMoney(val,0)*/
			}else {
				var leftP=toMoney(val/Math.pow(10,PriceDot),0);
				if(isNaN(leftP))leftP="--";
				scalersLeft.push(leftP);//toMoney(val,0)
			}
			var percent = (val - preClose) * 100 / preClose;
			scalersRight.push(percent.toFixed(2) + '%');
		}
		var yx = new yAxis(yOptions);
		var yAxisPainter = new Painter(this.canvas.id, yx, scalersLeft);
		yAxisPainter.paint();

		var yPercentOptions = this.minsChart.yScalerRight;
		yPercentOptions.color = function (val) {
			return (val == '0.00%' ? 'black' : (val.charAt(0) == '-' ? 'green' : 'red'));
		};
		var yxPercent = new yAxis(yPercentOptions);
		var yxPercentPainter = new Painter(this.canvas.id, yxPercent, scalersRight);
		//yxPercentPainter.paint();


		//均线
		if (this.needPaintAvgPriceLine) {
			//生成移动均线数据
			var items = [];
			var totalVolume = 0;
			var totalAmount = 0;
			data.mins.each(function (item) {
				totalVolume += item.volume;
				totalAmount += item.amount;
				items.push(totalAmount / totalVolume);
			});
			lineOptions.lineColor = minsChartOptions.avgPriceLineColor;
			lineOptions.getItemValue = function (item) { return item; };
			linePainterImp = new linePainter(lineOptions,this.rateW);
			var painterAvg = new Painter(this.canvas.id, linePainterImp, { items: items });
			painterAvg.paint();
		}
		//console.log(this.needPaintAvgPriceLine);

		var me = this;
		var chartRegion = me.minsChart.region;

		function getY(x) {
			var index = Math.ceil((x - me.minsChart.region.x) * me.maxDotsCount / me.minsChart.region.width);
			var val;
			var isNewQuote;
			if (index >= 0 && index < data.mins.length) {
				val = data.mins[index].price;
				isNewQuote = false;
			} else {
				val = data.quote.price;
				isNewQuote = true;
			}

			if (me.canvas.tip) me.canvas.tip.dataContext = { data: data, isNewQuote: isNewQuote, index: index };
			var diff = val - preClose;
			var middleY = (me.minsChart.region.y + me.minsChart.region.height / 2);
			return middleY - diff * me.minsChart.region.height / 2 / priceLinePainter.maxDiff;
		}
		
	},

	fillTopText: function (data, minIndex) {		
		var quote = data.quote;
		if(typeof quote["prod"]=="undefined" || quote["prod"]=="undefined")quote["prod"]=prod;
		var pdno =quote["prod"];
		if(pdno=='S2SFC') return;
		//if(prodindex[pdno]) pdno=prodindex[pdno];
		//console.log("prod",prod);
		//console.log("prod",quote["prod"]);
		$("#PD_NO").html("产品代号："+pdno);
		$("#PD_NAME").html("产品名称："+getProdNameMonth(quote["prod"]));
		
		
	},
	fillTopTextNow: function (data,price, time) {
	}
};



var prodName = new Object(); 
prodName.HSI="恒生期指";
prodName.HSCE="国企期指";
prodName.IF300="沪深期指";
prodName.S2SFC="富時中國";

prodName.O1GC="纽约期金";
prodName.M1EC="欧元期货";
prodName.B1YM="迷你道琼";
prodName.N1CL="小轻原油";

prodName.WTX="台湾期指";
prodName.M1ES="SP500";
prodName.M1NQ="Nasdaq";
var monthName = new Object(); 
monthName.F="(1月)";
monthName.G="(2月)";
monthName.H="(3月)";
monthName.J="(4月)";
monthName.K="(5月)";
monthName.M="(6月)";
monthName.N="(7月)";
monthName.Q="(8月)";
monthName.U="(9月)";
monthName.V="(10月)";
monthName.X="(11月)";
monthName.Z="(12月)";
function getProdNameMonth(no){
	var pid=no.substring(0,no.length-1);
	var m=no.substring(pid.length);	
	//alert(m)
	return prodName[pid]+monthName[m];
}
function getProdName(pid){
	return prodName[pid];
}
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function showDetailList(data){
	//{"data":"WTXG|2014-02-12 10:26:10|846500|846300|846400|47263|, WTXG|2014-02-12 10:26:10|846500|846300|846500|47273|, WTXG|2014-02-12 10:26:15|846500|846300|846500|47274|, ","PriceDot":"2","type":"GP","success":"true"}
	//data":"WTXG|2014-02-12 10:26:10|846500|846300|846400|47263|
	var globTqty=0;
	var index=0;
	var ulArr=new Array();
	try{
		for(var i=0;i<data.length;i++){ 
			if(data[i].indexOf("|")>0){
				
				var ara=data[i].split("|")
				var dateTimeAra=ara[1].split(" ");
				var time=dateTimeAra[1];
				if(dateTimeAra.length<2)time=ara[1];

				//if (obj.hasOwnProperty(ara[1]))continue;
				var tqty=ara[5];
				var sqty=tqty-globTqty;
				var price=toMoney(ara[4]/Math.pow(10,PriceDot),DotLength);
				
				var diff = toMoney((ara[4] - LastPrice),0);
				var diffhtml = toMoney((ara[4] - LastPrice)/Math.pow(10,PriceDot),DotLength);

				var isRise = diff > 0;
				var isEqual = diff == 0;
				var isFall = diff < 0;
				var txtRiseFall =  toMoney(diff * 100 / LastPrice,2);// + '%';

				var className="co_t_ba";
				if(isRise)className="co_t_ra";
				else if(isFall)className="co_t_ga";




				if(sqty==0)continue;
				globTqty=tqty;
				if(sqty==tqty)sqty="--";
				var str='<li class="wi_57 co_t_ba">'+time+'</li><li class="wi_48 '+className+'">'+price+'</li><li class="wi_44 '+className+'">'+diffhtml+'</li><li class="wi_48 '+className+'">'+txtRiseFall+'</li><li class="wi_40 co_t_ba">                        '+sqty+'</li><li class="wi_53 co_t_ba">'+tqty+'</li>';
			ulArr.push(str);
			}
		}

	}catch(e){
		console.log(data);
	}
	
	for(var i=0;i<13;i++){ 
		var size=ulArr.length;
		var str="";
		if(i<size)str=ulArr[size-i-1];
		$("#detail_ul_"+i).html(str)
	}



}