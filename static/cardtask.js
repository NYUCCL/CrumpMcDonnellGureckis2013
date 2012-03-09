
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

function insert_hidden_into_form(findex, name, value ) {
    var form = document.forms[findex];
    var hiddenField = document.createElement('input');
    hiddenField.setAttribute('type', 'hidden');
    hiddenField.setAttribute('name', name);
    hiddenField.setAttribute('value', value );
    form.appendChild( hiddenField );
}


// Preload images (not currently in use)
function imagepreload(src) 
{
	var heavyImage = new Image(); 
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
	var shufflelocations = new Array();
	for (var i=0; i<arr.length; i++) {
		shufflelocations.push(i);
	}
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
function shuffle( arr, exceptions ) {
	var i;
	exceptions = exceptions || [];
	var shufflelocations = new Array();
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
	var except = exceptions ? exceptions : [];
	var shufflelocations = new Array();
	for (i=0; i<arr.length; i++) {
		if (except.indexOf(i)==-1) { shufflelocations.push(i); }
	}
	
	for (i=shufflelocations.length-1; i>=0; --i) {
		var loci = shufflelocations[i],
			locj = shufflelocations[randrange(0,i+1)],
			tempi = arr[loci],
			tempj = arr[locj];
		arr[loci] = tempj;
		arr[locj] = tempi;
	}
	
	return arr;
}


// Mean of booleans (true==1; false==0)
function boolpercent(arr) {
	var count = 0;
	for (var i=0; i<arr.length; i++) {
		if (arr[i]) { count++; } 
	}
	return 100* count / arr.length;
}

// View functions
function appendtobody( tag, id, contents ) {
	var el = document.createElement( tag );
	el.id = id;
	el.innerHTML = contents;
	return el;
}

// Data submission
// NOTE: Ended up not using this.
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
var ncards = 8,
    cardnames = [
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
	"static/images/STIM15.PNG"],
	categorynames= [ "A", "B" ];

// Interface variables
var cardh = 180, cardw = 140, upper = 0, left = 0, imgh = 100, imgw = 100;


// Task objects
var testobject;

// Tasks
catfuns = [
	function (num) {
		// Shepard type I
		//0  0 0 0 - 0
		//1  0 0 1 - 1
		//2  0 1 0 - 0
		//3  0 1 1 - 1
		//4  1 0 0 - 0
		//5  1 0 1 - 1
		//6  1 1 0 - 0
		//7  1 1 1 - 1

		return num % 2;
	},
	function (num) {
		// Shepard type II
		//0  0 0 0 - 0
		//1  0 0 1 - 1
		//2  0 1 0 - 1
		//3  0 1 1 - 0
		//4  1 0 0 - 0
		//5  1 0 1 - 1
		//6  1 1 0 - 1
		//7  1 1 1 - 0

		return ((num&2)/2)^(num&1);
	},
	function (num) {
		// Shepard type III
		//0  0 0 0 - 1
		//1  0 0 1 - 0     E
		//2  0 1 0 - 1     E
		//3  0 1 1 - 0
		//4  1 0 0 - 1
		//5  1 0 1 - 1  E
		//6  1 1 0 - 0  E
		//7  1 1 1 - 0

		if (num & 1) { return ((num%8)===5) ? 1 : 0; }
		else { return (num % 8)===6 ? 0 : 1; }
	},
	function (num) {
		// Shepard type IV
		//0  0 0 0 - 1
		//1  0 0 1 - 1        E
		//2  0 1 0 - 1    E
		//3  0 1 1 - 0 E
		//4  1 0 0 - 1 E
		//5  1 0 1 - 0    E
		//6  1 1 0 - 0       E
		//7  1 1 1 - 0

		var score = 0; // prototypicality score
		if ( num & 1 ) { score++; }
		if ( num & 2 ) { score++; }
		if ( num & 4 ) { score++; }
		return (score>=2) ? 0 : 1;
	},
	function (num) {
		// Shepard type V
		//0  0 0 0 - 1
		//1  0 0 1 - 0
		//2  0 1 0 - 1
		//3  0 1 1 - 0
		//4  1 0 0 - 1
		//5  1 0 1 - 0
		//6  1 1 0 - 0  E
		//7  1 1 1 - 1  E

		if (num & 1) { return (num%8 === 7) ? 1 : 0; }
		else { return (num%8 === 6) ? 0 : 1; }
	},
	function (num) {
		// Shepard type VI
		//0  0 0 0 - 1
		//1  0 0 1 - 0
		//2  0 1 0 - 0
		//3  0 1 1 - 1
		//4  1 0 0 - 0
		//5  1 0 1 - 1
		//6  1 1 0 - 1
		//7  1 1 1 - 0        
        
		if (num & 1) { return (num&2)^((num&4)/2) ? 1:0; }
		else { return (num&2)^((num&4)/2) ? 0:1; }
	}
];
var catfun;

// Stimulus counterbalancer
getstim = function(theorystim) {
	console.assert( theorystim < 8, "Stim >=8 ("+theorystim+")");
	console.assert( theorystim >= 0, "Stim less than 0 ("+theorystim+")");
	var flippedstim = theorystim^condition.dimvals;
	var bits = new Array();
	for (var i=0; i<4; i++) {
		bits.push( flippedstim&Math.pow(2,i) ? 1 : 0 );
	}
	
	changeorder(bits, condition.dimorder);
	
	var multiples = [1, 2, 4, 8];
	var ret = 0;
	for (i=0; i<=3; i++) {
		ret += multiples[i] * bits[i];
	}
	return ret;
};

// Mutable global variables
var responsedata = [],
    currentblock = 1,
    currenttrial = 1,
    datastring = "",
    lastperfect = false;

// Data handling functions
// TODO: consider not recording the first five columns every trial. 
function recordinstructtrial (instructname, rt ) {
	trialvals = [subjid, condition.traintype, condition.rule, condition.dimorder, condition.dimvals, "INSTRUCT", instructname, rt];
	datastring = datastring.concat( trialvals, "\n" );
}
function recordtesttrial (theorystim, actualstim, correct, resp, hit, rt ) {
	trialvals = [subjid, condition.traintype, condition.rule, condition.dimorder, condition.dimvals, currentblock, currenttrial,  "TEST", theorystim, actualstim, correct, resp, hit, rt];
	datastring = datastring.concat( trialvals, "\n" );
	currenttrial++;
}

/********************
* HTML snippets
********************/
var pages = {};

var showpage = function(pagename) {
	$('body').html( pages[pagename] );
};

var pagenames = [
	"postquestionnaire",
	"test",
	"instruct1",
	"instructCatExample",
	"instructCatColor",
	"instructCatStripe",
	"instructTest",
	"instructTest2",
	"instructDimColor",
	"instructDimBorder",
	"instructDimDots",
	"instructDimStripe",
	"instructDimAll",
	"instructFinal",
	"instructFinal2"
];




/************************
* CODE FOR INSTRUCTIONS *
************************/
var Instructions = function() {
	var that = this;
	var screens = [
			"instruct1",
			"instructCatExample",
			"instructCatColor",
			"instructCatStripe",
			"instructTest",
			"instructTest2",
			"instructDimColor",
			"instructDimBorder",
			"instructDimDots",
			"instructDimStripe",
			"instructDimAll",
			"instructFinal",
			"instructFinal2" 
		],
		currentscreen = "",
		timestamp;

	this.recordtrial = function() {
		rt = (new Date().getTime()) - timestamp;
		recordinstructtrial( currentscreen, rt  );
	};
	
	this.nextForm = function () {
		var next = screens.splice(0, 1)[0];
		currentscreen = next;
		showpage( next );
		timestamp = new Date().getTime();
		if ( screens.length === 0 ) $('.continue').click(function() {
			that.recordtrial();
			that.startTest();
		});
		else $('.continue').click( function() {
			that.recordtrial();
			that.nextForm();
		});
	};
	this.startTest = function() {
		startTask();
		testobject = new TestPhase();
	};
	this.nextForm();
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
	    prescard,
	    testcardsleft = new Array();
	
	this.hits = new Array();
	
	var acknowledgment = '<p>Thanks for your response!</p>';
	var buttons = '<p id="prompt">Which group does the object belong to?\
		<div id="inputs">\
				<input type="button" id="CategoryA" value="A">\
				<input type="button" id="CategoryB" value="B">\
		</div>';
	showpage( 'test' );
	
	var addbuttons = function() {
		buttonson = new Date().getTime();
		$('#query').html( buttons );
		$('input').click( function(){
			catresponse(this.value);
		} );
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
		var hitmessage = '<span style="color: #0F0;"><p style="font-size: 42px;">CORRECT.</p>';
		var missmessage = '<span style="color: #F00;"><p style="font-size: 42px;">INCORRECT!</p>';
		var respmessages = ['<p style="font-size: 24px">The correct answer was A.</p></span>',
                            '<p style="font-size: 24px">The correct answer was B.</p></span>'];
		$('#query').html((washit ? hitmessage : missmessage) + respmessages[actual]);
		setTimeout( function() {
				$("#stim").hide();
				$("#query").hide();
				setTimeout( nextcard, 500);
			}, 
			1000);
		that.hits.push( washit );
		recordtesttrial (prescard, getstim(prescard), actual, resp, washit, rt );
		return false;
	};
	
	
	var finishblock = function() {
		currentblock++;
		var done = false;
		if (currentblock > condition.maxblocks) done = true;
		else {
			if ( boolpercent(that.hits)==100 ) {
				if ( lastperfect ) done = true;
				lastperfect = true;
			}
			else lastperfect=false;
		}
		if (done) givequestionnaire();
		else {
        	$.ajax("inexpsave", {
        			type: "POST",
        			async: true,
        			data: {subjId: subjid, dataString: datastring}
        	});

			$('body').html('<h1>Test phase Complete</h1>\
				<p>Block complete! <b>You have completed ' + (currentblock-1) + ' out of ' + condition.maxblocks + ' total test rounds</b>.\
				 You got ' + boolpercent(that.hits) + '% correct.</p>' +
				 ((boolpercent(that.hits)==100) ? '\r<p>Just one more round like that and you\'ll be done!' : '\r<p>If you can get two in a row at 100% you can stop early!') + 
				 '<p>Press "Continue" to move on to the next block.</p>\
				  <input type="button" id="continue" value="Continue"></input>');
			$('#continue').click( function(){ testobject = new TestPhase(); } );
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
	testcardsleft = [ 0,1,2,3,4,5,6,7,  0,1,2,3,4,5,6,7 ];
	shuffle(testcardsleft);
	$("#stim").attr("width", imgw);
	$('#query').hide();
	nextcard();
	return this;
};

/*************
* Finish up  *
*************/
var givequestionnaire = function() {
	var timestamp = new Date().getTime();
	showpage('postquestionnaire');
	recordinstructtrial( "postquestionnaire", (new Date().getTime())-timestamp );
	$("#continue").click(function () {
		finish();
		submitquestionnaire();
	});
	// $('#continue').click( function(){ trainobject = new TrainingPhase(); } );
	// postback();
};
var submitquestionnaire = function() {
	$('textarea').each( function(i, val) {
		datastring = datastring.concat( "\n", this.id, ":",  this.value);
	});
	$('select').each( function(i, val) {
		datastring = datastring.concat( "\n", this.id, ":",  this.value);
	});
	insert_hidden_into_form(0, "subjid", subjid );
	insert_hidden_into_form(0, "data", datastring );
	$('form').submit();
};

var startTask = function () {
	$.ajax("inexp", {
			type: "POST",
			async: true,
			data: {subjId: subjid}
	});
	// Provide opt-out 
	window.onbeforeunload = function(){
    	$.ajax("quitter", {
    			type: "POST",
    			async: false,
    			data: {subjId: subjid, dataString: datastring}
    	});
		alert( "By leaving this page, you opt out of the experiment.  You are forfitting your payment. Please confirm that this is what you meant to do." );
		return "Are you sure you want to leave the experiment?";
	};
};

var finish = function () {
	window.onbeforeunload = function(){ };
};

// vi: et! ts=4 sw=4
