
/**********************
* Domain general code *
**********************/


// Helper functions

// Assert functions stolen from 
// http://aymanh.com/9-javascript-tips-you-may-not-know#assertion
function AssertException(message) { this.message = message; }
AssertException.prototype.toString = function () {
	return 'AssertException: ' + this.message;
};

function assert(exp, message) {
	if (!exp) {
	  throw new AssertException(message);
	}
}


// Preload images
function imagepreload(src) 
{
	heavyImage = new Image(); 
	heavyImage.src = src;
}

/** 
 * SUBSTITUTE PLACEHOLDERS WITH string values 
 * @param {String} str The string containing the placeholders 
 * @param {Array} arr The array of values to substitute 
 * From Fotiman on this forum:
 * http://www.webmasterworld.com/javascript/3484761.htm
 */ 
function substitute(str, arr) 
{ 
	var i, pattern, re, n = arr.length; 
	for (i = 0; i < n; i++) { 
		pattern = "\\{" + i + "\\}"; 
		re = new RegExp(pattern, "g"); 
		str = str.replace(re, arr[i]); 
	} 
	return str; 
} 

function randrange ( lower, upperbound ) {
	// Finds a random integer from 'lower' to 'upperbound-1'
	return Math.floor( Math.random() * upperbound + lower );
}

// We want to be able to alias the order of stimuli to a single number which
// can be stored and which can easily replicate a given stimulus order.
function changeorder( arr, ordernum ) {
	var thisorder = ordernum;
	for (i=arr.length-1; i>=0; --i) {
		var loci = shufflelocations[i];
		var locj = shufflelocations[thisorder%(i+1)];
		thisorder = Math.floor(thisorder/(i+1));
		var tempi = arr[loci];
		var tempj = arr[locj];
		arr[loci] = tempj;
		arr[locj] = tempi;
	}
	return arr;
}

// Fisher-Yates shuffle algorithm.
// modified from http://sedition.com/perl/javascript-fy.html
// TODO: make sure this works okay.
function shuffle( arr, exceptions ) {
	var i;
	exceptions = exceptions || [];
	shufflelocations = new Array();
	for (i=0; i<arr.length; i++) {
		if (exceptions.indexOf(i)==-1) { shufflelocations.push(i); }
	}
	for (i=shufflelocations.length-1; i>=0; --i) {
		var loci = shufflelocations[i];
		var locj = shufflelocations[randrange(0, i+1)];
		var tempi = arr[loci];
		var tempj = arr[locj];
		arr[loci] = tempj;
		arr[locj] = tempi;
	}
	return arr;
}

// This function swaps two array members at random, provided they are not in
// the exceptions list.
function swap( arr, exceptions ) {
	var i;
	exceptions = exceptions ? exceptions : [];
	shufflelocations = new Array();
	for (i=0; i<arr.length; i++) {
		if (exceptions.indexOf(i)==-1) { shufflelocations.push(i); }
	}
	var loc1 = shufflelocations.splice(
			randrange(0, shufflelocations.length), 1);
	var loc2 = shufflelocations.splice(
			randrange(0, shufflelocations.length), 1);
	var temp1 = arr[loc1];
	var temp2 = arr[loc2];
	arr[loc1] = temp2;
	arr[loc2] = temp1;
	return arr;
}


// Mean of booleans (true==1; false==0)
function boolpercent(arr) {
	count = 0;
	for (i=0; i<arr.length; i++) {
		if (arr[i]) { count++; } 
	}
	return 100* count / arr.length;
}

// View functions
function appendtobody( tag, id, contents ) {
	el = document.createElement( tag );
	el.id = id;
	el.innerHTML = contents;
	return el;
}

// Data submission
function posterror() { alert( "There was an error. TODO: Prompt to resubmit here." ); }
function submitdata() {
	$.ajax("submit", {
			type: "POST",
			async: false,
			data: {datastring: datastring},
			// dataType: 'text',
			success: thanks,
			error: posterror
	});
}


/********************
* TASK-GENERAL CODE *
********************/

// Globals defined initially.

// Stimulus info
ncards = 8;
var cardnames = [
	"static/images/STIM00.PNG",
	"static/images/STIM01.PNG",
	"static/images/STIM02.PNG",
	"static/images/STIM03.PNG",
	"static/images/STIM04.PNG",
	"static/images/STIM05.PNG",
	"static/images/STIM06.PNG",
	"static/images/STIM07.PNG",
	"static/images/STIM08.PNG",
	"static/images/STIM09.PNG",
	"static/images/STIM10.PNG",
	"static/images/STIM11.PNG",
	"static/images/STIM12.PNG",
	"static/images/STIM13.PNG",
	"static/images/STIM14.PNG",
	"static/images/STIM15.PNG"];
var categorynames= [ "A", "B" ];

// Interface variables
var cardh = 180, cardw = 140, upper = 0, left = 0, imgh = 100, imgw = 100;


// Task objects
var trainobject, testobject;

// Subject info, including condition and counterbalance codes.
// TODO: fill this in using hidden forms or something
var subjid = 0;
var condition = {
	traintype: randrange(0,2) , // 0=active, 1=passive
	rule: randrange(0,6), // type I-VI -> 0-5.
	dimorder: randrange(0,24), // 0-23; which order to order the dimensions
	dimvals: randrange(0,16)  // 0-16 whether a '0' means 0 or 1 in terms of the stim.
};

// Tasks
catfuns = [
	function (num) {
		// Shepard type I
		return num % 2;
	},
	function (num) {
		// Shepard type II
		return ((num&2)/2)^(num&1);
	},
	function (num) {
		// Shepard type III
		if (num & 1) { return ((num%8)===1) ? 0 : 1; }
		else { return (num % 8)===2 ? 1 : 0; }
	},
	function (num) {
		// Shepard type IV
		score = 0; // prototypicality score
		if ( num & 1 ) { score++; }
		if ( num & 2 ) { score++; }
		if ( num & 4 ) { score++; }
		return (score>=2) ? 0 : 1;
	},
	function (num) {
		// Shepard type V
		if (num & 1) { return (num%8 === 7) ? 1 : 0; }
		else { return (num%8 === 6) ? 0 : 1; }
	},
	function (num) {
		// Shepard type VI
		if (num & 1) { return (num&2)^((num&4)/2) ? 1:0; }
		else { return (num&2)^((num&4)/2) ? 0:1; }
	}
];
var catfun = catfuns[condition.rule];

// Stimulus counterbalancer
getstim = function(theorystim) {
	console.assert( theorystim < 8, "Stim >=8 ("+theorystim+")");
	console.assert( theorystim >= 0, "Stim less than 0 ("+theorystim+")");
	flippedstim = theorystim^condition.dimvals;
	bits = new Array();
	oldbits = new Array();
	for (i=0; i<4; i++) {
		bits.push( flippedstim&Math.pow(2,i) ? 1 : 0 );
		oldbits.push( flippedstim&Math.pow(2,i) ? 1 : 0 );
	}
	
	changeorder(bits, condition.dimorder);
	
	var multiples = [1, 2, 4, 8];
	var ret = 0;
	for (var i=0; i<=3; i++) {
		ret += multiples[i] * bits[i];
	}
	return ret;
};

// Mutable global variables
var responsedata = [],
    currentblock = 0,
    currenttrial = 0,
    datastring = "",
    lastperfect = false;

// Data handling functions
// TODO: consider not recording the first five columns every trial. 
function recordtraintrial (theorystim, actualstim, category, loc, rt ) {
	trialvals = [subjid, currentblock, currenttrial, condition.traintype, condition.rule, condition.dimorder, condition.dimvals, "TRAINING", theorystim, actualstim, category, loc, rt];
	datastring = datastring.concat( trialvals, "\n" );
	currenttrial++;
}
function recordtesttrial (theorystim, actualstim, correct, resp, hit, rt ) {
	trialvals = [subjid, currentblock, currenttrial, condition.traintype, condition.rule, condition.dimorder, condition.dimvals, "TEST", theorystim, actualstim, correct, resp, hit, rt];
	datastring = datastring.concat( trialvals, "\n" );
	currenttrial++;
}

/********************
* HTML snippets
********************/
var consentpage,
    instruct1,
    instruct2,
    instruct3,
    testpage,
    debriefingbody,
    thanksbody,
    activetaskbody,
    passivetaskbody;
$( function() {
    $.get( "postquestionnaire.html", "html", function(page) { postquiz=page; } );
    $.get( "debriefing.html", "html", function(page) { debriefingbody=page; } );
    $.get( "thanks.html", "html", function(page) { thanksbody=page; } );
    $.get( "test.html", "html", function(page) { testpage=page; } );
    $.get( "active.html", "html", function(page) { activetaskbody=page; } );
    $.get( "passive.html", "html", function(page) { passivetaskbody=page; } );
});

/********************
* (relatively) static pages
********************/
function debriefing () {
	// TODO: make sure the forms are filled out.
	$('body').html( debriefingbody );
}
function thanks() {
	$('body').html( thanksbody );
}

/************************
* CODE FOR INSTRUCTIONS *
************************/
var Instructions = function() {
	var that = this;
	screens = [consent, instruct1, instruct2, instruct3].reverse();
	
	this.nextForm = function () {
		next = screens.pop();
		$('body').html( next );
        if ( screens.length === 0 ) $('.continue').click( that.startTraining );
        else $('.continue').click( that.nextForm );
	}
	this.startTraining = function() {
		trainobject = new TrainingPhase();
	}
	this.nextForm();
}


/********************
* CODE FOR TRAINING *
********************/

var TrainingPhase = function() {
	var i; // just initializing the iterator dummy
	var that = this; // make 'this' accessble by privileged methods
	var cardattributes = {};
	
	var sampleunits = 16;
	
	// Mutables
	var lock = false;
	var animating = false;
	var cards = new Array();
	var shuffletimestamp;
	
	// View variables
	var ncardswide = 4, ncardstall = 2;
	
	// Rewrite html
	if ( condition.traintype===0 ) {
		$('body').html(activetaskbody);
	}
	else{
		$('body').html(passivetaskbody);
	}
	
	// Canvas for the cards.
	var nowX, nowY, w = ncardswide*cardw, h = ncardstall*cardh, r=30;
	//var cardpaper = Raphael(document.getElementById("cardcanvas"), w, h);
	var cardpaper = Raphael(document.getElementById("cardcanvas"), w, h);
	
	// Canvas for the timer.
	var timertotalw = w*2/3;
	var timertotalh = 50;
	var w2 = timertotalw, h2 = timertotalh;
	var timerpaper = Raphael(document.getElementById("timercanvas"), w2, h2);
	
	var presentations = [0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7];
	shuffle(presentations);
	this.next = presentations.pop();
	
	var textsize = 42;
	var timerects = timerpaper.set();
	timerectw = timertotalw / (sampleunits*2-2+10);
	var timetext = timerpaper.text( textsize/2, h2/2, sampleunits ).attr({fill:"white","font-size":textsize});
	for ( i=0; i < sampleunits; i ++) {
		timerects.push(
			timerpaper.rect(
				timerectw * i * 2 + textsize*1.5,
				0,
				timerectw, timertotalh, [5]).attr({fill:"red" }));
	}
	
	// Category labels are just the letters.
	
	// Card locations are randomized.
	this.cardlocs = new Array();
	for ( i=0; i < ncards; i ++ ){ 
		this.cardlocs.push( i ); 
	}
	shuffle( this.cardlocs );
	
	// recent cards; will not move after next selection.
	this.lastcards = [undefined,undefined];
	
	// Card hilighting functions:
	var turnon = function(cardid){
		return function() {
			cards[cardid][0].attr({"stroke-opacity": 100});
		};
	};
	var turnoff = function(cardid){
		return function() {
			cards[cardid][0].attr({"stroke-opacity": 0});
		};
	};
	this.indicateCard = function(cardid) {
		that.lock = true;
		turnon();
		setTimeout(turnoff(cardid), 100);
		setTimeout(turnon(cardid), 200);
		setTimeout(turnoff(cardid), 300);
		setTimeout(turnon(cardid), 400);
		setTimeout(function(){ lock=false; }, 400);
	};
	
	this.cardclick = function (cardid) {
		return function() {
			if (condition.traintype===1) {
				if ( that.next != cardid ) { return false; }
			}
			if ( ! timerects.length ) { return false; }
			if ( lock ) {  return false; }
			if (condition.traintype===0) {
				turnon(cardid)();
			}
			else {
				that.next = presentations.pop();
			}
			lock = true;
			cards[cardid][2].show();
			setTimeout(
				function(){
					cards[cardid][2].hide();
					turnoff(cardid)();
					timerects.pop().attr({fill: "gray"});
					timetext.attr({text:timerects.length});
					if ( timerects.length===0 ) {
						$('body').html('<h1>Training Complete</h1>\
							<p>Training complete! Press "Continue" to move on to the test phase.</p>\
							<input type="button" id="continue" value="Continue"></input>');
						$('#continue').click( function(){ testobject = new TestPhase(); } );
						$('#continue').attr('style', 'width: auto;');
						$("p").attr("style", "font-size: 150%");
						return true;
					}
					var callback = function () {
						if (condition.traintype===1) {
							that.indicateCard( that.next );
						}
						else setTimeout( function(){ lock=false; }, 400); 
					};
					shuffletimestamp  = new Date().getTime();
					shufflecards( callback, that.lastcards );
					return true;
				},
				1500);
			var actualstim = cardattributes[cardid].actualstim,
			    theorystim = cardattributes[cardid].theorystim,
			    catnum = cardattributes[cardid].catnum,
			    loc = cardattributes[cardid].getlocation();
			rt = new Date().getTime() - shuffletimestamp;
			recordtraintrial(theorystim, actualstim, catnum, loc, rt);
			that.lastcards.splice(0,1);
			that.lastcards.push( cardid );
			return true;
		};
	};
	
	var loc_coords = function ( loci ) {
		var x = cardw * (loci % 4) + left;
		var y = cardh*Math.floor(loci/4) + upper;
		var imgoffset = (cardw-imgw)/2;
		return {
			x: x,
			y: y,
			outerx: x + (imgoffset/2),
			outery: y + (imgoffset/2),
			cardx: x + imgoffset,
			cardy: y + imgoffset,
			labelx: x + cardw/2,
			labely: (y+imgoffset + y+(imgoffset/2) + cardh-imgoffset + imgh)/2
		};
	};
	
	for ( i=0; i < ncards; i ++) {
		cards[i] = cardpaper.set();
		coords = loc_coords( this.cardlocs[i] );
		var thisleft = coords.x, thistop = coords.y;
		var imgoffset = (cardw-imgw)/2;
		
		cardattributes[i] = {
			"theorystim": i,
			"actualstim": getstim(i),
			"catnum": catfun(i),
			"getlocation": function() { return that.cardlocs[ this.theorystim ]; }
		};
		// Add outside rectangle ('card')
		cards[i].push(
			cardpaper.rect( 
				thisleft + (imgoffset/2),
				thistop + (imgoffset/2),
				imgw + imgoffset,
				cardh - imgoffset).attr(
					{stroke: "red", "stroke-width": "5px", "stroke-opacity": 0}
				));
		// Add actual stim
		cards[i].push(
			cardpaper.image(
				cardnames[cardattributes[i].actualstim], 
				thisleft + imgoffset, 
				thistop+imgoffset, 
				imgw, imgh));
		// Add label (hidden initially)
		cards[i].push(
				cardpaper.text(
					thisleft + cardw/2,
					(thistop+imgoffset + thistop+(imgoffset/2) + cardh-imgoffset + imgh)/2,
					categorynames[cardattributes[i].catnum]).attr(
						{ fill: "white", "font-size":36 }).hide());
		
		cards[i].click( this.cardclick(i) );
	}
	
	var shufflecards = function(callback, exceptions) {
		swap( that.cardlocs, exceptions );
		that.animating = true;
		for ( var i=0; i < ncards; i ++){
			coords = loc_coords( that.cardlocs[i] );
			cards[i][0].attr({ x: coords.outerx, y: coords.outery });
			cards[i][1].animate({ x: coords.cardx, y: coords.cardy }, 500, "<", callback);
			cards[i][2].attr({ x: coords.labelx, y: coords.labely });
			// outerrect = cards[i][0];
		}
		return true;
	};
	
	shuffletimestamp  = new Date().getTime();
	if ( condition.traintype===1 ) { this.indicateCard(this.next); }
	
	// Usually this would be a dictionary of public methods but 
	// I'm exporting the whole thing, which will make everything accessible.
	return this;
};

/********************
* CODE FOR TEST     *
********************/

var TestPhase = function() {
	var i,
	    that = this, // make 'this' accessble by privileged methods
	    lock,
	    stimimage,
	    buttonson,
	    testcardsleft = new Array();
	
	this.hits = new Array();
	
	acknowledgment = '<p>Thanks for your response!</p>';
	buttons = '<p id="prompt">Which category does the object belong to?\
		<div id="inputs">\
				<input type="button" id="CategoryA" value="A">\
				<input type="button" id="CategoryB" value="B">\
		</div>';
	$('body').html( testpage );
	
	var addbuttons = function() {
		buttonson = new Date().getTime();
		$('#query').html( buttons );
		$('input').click( function(){catresponse(this.value);} );
		$('#query').show();
	};
	
	catresponse = function (buttonid){
		if (lock) { return false; }
		var rt = new Date().getTime() - buttonson,
		    washit,
		    resp = categorynames.indexOf(buttonid), // should be "A" or "B"
		    actual = catfun(prescard); // should be "A" or "B"
		washit = resp === actual;
		lock = true;
		$('#query').html(acknowledgment);
		setTimeout( function() {
				$("#stim").hide();
				$("#query").hide();
			}, 
			500);
		setTimeout( nextcard, 1000);
		that.hits.push( washit );
		recordtesttrial (prescard, getstim(prescard), actual, resp, washit, rt );
		return false;
	};
	
	var givequestionnaire = function() {
		$('body').html(postquiz);
		// $('#continue').click( function(){ trainobject = new TrainingPhase(); } );
		$('#continue').attr('style', 'width: auto;');
		$("p").attr("style", "font-size: 150%");
		// postback();
	};
	
	var finishblock = function() {
		currentblock++;
		done = false;
		if ( boolpercent(that.hits)==100 ) {
			if ( lastperfect ) done = true;
			lastperfect = true;
		}
		else lastperfect=false;
		if (done) givequestionnaire();
		else {
			$('body').html('<h1>Test phase Complete</h1>\
				<p>Test phase complete! You got ' + boolpercent(that.hits) + '% correct.</p>' +
				((boolpercent(that.hits)==100) ? '\r<p>Just one more round like that and you\'ll be done!' : "") +
				'<p>Press "Continue" to move on to the next training block.</p>\
				<input type="button" id="continue" value="Continue"></input>');
			$('#continue').click( function(){ trainobject = new TrainingPhase(); } );
			$('#continue').attr('style', 'width: auto;');
			$("p").attr("style", "font-size: 150%");
			// postback();
		}
	};
	
	var nextcard = function () {
		var done = false;
		if (! testcardsleft.length) {
			finishblock();
		}
		else {
			prescard = testcardsleft.pop();
			//stimimage = testcardpaper.image( cardnames[getstim(prescard)], 0, 0, imgw, imgh);
			$("#stim").attr("src", cardnames[getstim(prescard)]);
			$('#stim').show();
			setTimeout(
				function(){
					lock=false;
					addbuttons();
				},
				500);
		}
	};
	
	//testcardpaper = Raphael(document.getElementById("testcanvas"), w, h);
	testcardsleft = [0,1,2,3,4,5,6,7];
	shuffle(testcardsleft);
	$("#stim").attr("width", imgw);
	$('#query').hide();
	givequestionnaire();
	nextcard();
	return this;
};


/*********************
* Get things started *
********************/

// Provide opt-out 
//$(window).bind('beforeunload', function(){
//	alert( "By leaving this page, you opt out of the experiment. Please confirm that this is what you meant to do." );
//	return ("Are you sure you want to leave the experiment?");
//});
$(window).load( function(){
    // Load resources then run the exp
    $.get( "consent.html", "html", function(page) { consent=page; } );
    $.get( "activeInstruct1.html", "html", function(page) { instruct1=page; } );
    $.get( "activeInstruct2.html", "html", function(page) { instruct2=page; } );
    $.get( "activeInstruct3.html", "html", function(page) { instruct3=page; } );
    $.get( "postquestionnaire.html", "html", function(page) { postquiz=page; } );
    $.get( "test.html", "html", function(page) { testpage=page; } );
    $.get( "active.html", "html", function(page) { activetaskbody=page; } );
    $.get( "passive.html", "html", function(page) { passivetaskbody=page; instructobject = new Instructions();} );
});



// vi: et! ts=4 sw=4
