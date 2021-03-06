
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
function imagepreload(src) {
	var im = new Image(); 
	im.src = src;
}

/** 
 * SUBSTITUTE PLACEHOLDERS WITH string values 
 * @param {String} str The string containing the placeholders 
 * @param {Array} arr The array of values to substitute 
 * From Fotiman on this forum:
 * http://www.webmasterworld.com/javascript/3484761.htm
 */ 
function substitute(str, arr) { 
	var i, pattern, re, n = arr.length; 
	for (i = 0; i < n; i++) { 
		pattern = "\\{" + i + "\\}"; 
		re = new RegExp(pattern, "g"); 
		str = str.replace(re, arr[i]); 
	} 
	return str; 
}

// Finds a random integer from 'lower' to 'upperbound-1'
function randrange ( lower, upperbound ) {
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
	"static/images/STIM00.png",
	"static/images/STIM01.png",
	"static/images/STIM02.png",
	"static/images/STIM03.png",
	"static/images/STIM04.png",
	"static/images/STIM05.png",
	"static/images/STIM06.png",
	"static/images/STIM07.png",
	"static/images/STIM08.png",
	"static/images/STIM09.png",
	"static/images/STIM10.png",
	"static/images/STIM11.png",
	"static/images/STIM12.png",
	"static/images/STIM13.png",
	"static/images/STIM14.png",
	"static/images/STIM15.png"],
	categorynames= [ "A", "B" ];
var cardsshown = [ 0,1,2,3,4,5,6,7,  0,1,2,3,4,5,6,7 ];

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
		//1  0 0 1 - 0	 E
		//2  0 1 0 - 1	 E
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
		//1  0 0 1 - 1		E
		//2  0 1 0 - 1	E
		//3  0 1 1 - 0 E
		//4  1 0 0 - 1 E
		//5  1 0 1 - 0	E
		//6  1 1 0 - 0	   E
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
	assert( theorystim < 8, "Stim >=8 ("+theorystim+")");
	assert( theorystim >= 0, "Stim less than 0 ("+theorystim+")");
	var flippedstim = theorystim^condition.dimvals; // Here the stim identities are flipped
	assert( flippedstim <8, "Agh" );
	var bits = new Array();
	for (var i=0; i<3; i++) {
		bits.push( flippedstim&Math.pow(2,i) ? 1 : 0 );
	}
	
	changeorder(bits, condition.dimorder);
	
	var multiples = [1, 2, 4];
	var ret = 0;
	for (i=0; i<3; i++) {
		ret += multiples[i] * bits[i];
	}
	return ret;
};

// Mutable global variables
var responsedata = [],
    currentblock = 1,
    instructround = 0,
    currenttrial = 1,
    totalmisses = 0,
    datastring = "",
    lastperfect = false;

// Data handling functions

// Records RT for each instruction trial
function recordinstructtrial (instructname, rt, correct ) {
	if (typeof correct=="undefined") {
		correct = "na";
	}
	trialvals = [subjid, condition.traintype, condition.rule, condition.dimorder, condition.dimvals, "INSTRUCT", instructround, instructname, correct, rt];
	datastring = datastring.concat( trialvals, "\n" );
}

// Records resp and RT for each instruction trial. 
function recordtesttrial (theorystim, actualstim, correct, resp, hit, rt ) { 
	if (! hit) totalmisses += 1;
	trialvals = [subjid, condition.traintype, condition.rule,
			  condition.dimorder, condition.dimvals, currentblock,
			  currenttrial, "TEST", theorystim, actualstim, correct, resp, hit,
			  rt];
	datastring = datastring.concat( trialvals, "\n" );
	currenttrial++;
}

//  Writes the form ids and their responses to the datafile. 
function recordFormFields () {
    var fields = {};
    
    var extractfun = function(i, val) { 
		var value;
		if (this.id !== this.value) value = this.value; 
		else value = this.checked;
		datastring = datastring.concat( "\n", this.id, ":",  value);
    };
    
	$('textarea').each( extractfun );
	$('select').each( extractfun );
	$('input').each( extractfun );

    return fields;
}

//  Returns the form contents as a mapping.
function getFormFields () {
    var fields = {};
    
    var extractfun = function(i, val) { 
		var value;
		if (this.id !== this.value) value = this.value; 
		else value = this.checked;
		fields[this.id] = value; 
    };
    
	$('textarea').each( extractfun );
	$('select').each( extractfun );
	$('input').each( extractfun );
    
    return fields;
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
	"prequiz",
	"instruct1",
	"instructCatExample",
	"instructCatSize",
	"instructCatShape",
	"instructTest",
	"instructTest2",
	"instructDimShape",
	"instructDimSize",
	"instructDimTexture",
	"instructDimAll",
	"instructFinal",
	"instructFinal2",
	"starttask",
	"redoinstruct"
];




/************************
* CODE FOR INSTRUCTIONS *
************************/
var Instructions = function() {
	var that = this;
	var screens = [
			"instruct1",
			"instructCatExample",
			"instructCatSize",
			"instructCatShape",
			"instructTest",
			"instructTest2",
			"instructDimShape",
			"instructDimSize",
			"instructDimTexture",
			"instructDimAll",
			"instructFinal",
			"instructFinal2" 
		],
		currentscreen = "",
		timestamp;
	instructround++;
    
	this.recordtrial = function() {
		var rt = (new Date().getTime()) - timestamp;
		recordinstructtrial( currentscreen, rt  );
	};
	this.recordtest = function() {
		var rt = (new Date().getTime()) - timestamp;
		recordinstructtrial( "", rt  );
	};
	
	this.nextForm = function () {
		var next = screens.splice(0, 1)[0];
		currentscreen = next;
		showpage( next );
		timestamp = new Date().getTime();
		if ( screens.length === 0 ) $('.continue').click(function() {
			that.recordtrial();
			that.givePreQuiz();
		});
		else $('.continue').click( function() {
			that.recordtrial();
			that.nextForm();
		});
	};
	
    // Determine if the form has been filled out.
	var validateformfields = function (fields) {
		var missing = [];
		// Blocks to criterion
		if ( ! fields.criterion ) missing.push("criterion");
		if ( ! fields.ruleyes && ! fields.ruleno ) missing.push("rule");
		if ( ! fields.changeyes && ! fields.changeno ) missing.push("change");
		if ( ! fields.aidsno && ! fields.aidsyes ) missing.push("aids");
		if ( ! fields.fill && 
             ! fields.shape && 
             ! fields.size && 
             ! fields.pattern && 
             ! fields.borderstyle && 
             ! fields.bordercolor ) missing.push("features");
		return missing;
	};
	
	// checkformfields :: {fields} -> Bool
	var checkformfields = function (fields) {
		var correct = true;
		// Blocks to criterion
		if ( fields.criterion !== "2") correct = false;
		// There is a rule? y/n
		if ( ! fields.ruleyes ) correct = false;
		// Rule changes? y/n
		if ( ! fields.changeno ) correct = false;
		// Aids? y/n
		if ( ! fields.aidsno ) correct = false;
		// Stimuli Features
		// Target answers:
		if ( ! fields.fill ) correct = false;
		if ( ! fields.shape ) correct = false;
		if ( ! fields.size ) correct = false;
		// Lure answers:
		if (   fields.pattern ) correct = false;
		if (   fields.borderstyle ) correct = false;
		if (   fields.bordercolor ) correct = false;
		return correct;
	};
	
	this.givePreQuiz = function() {
		showpage( "prequiz" );
		timestamp = new Date().getTime();
		$("#continue").click(function () {
			if ( validateformfields( getFormFields() ).length > 0 ) {
				$("#warning").text("Please fill out all the fields before continuing.");
				return false;
			}
			var fields = getFormFields();
			
			var rt = (new Date().getTime()) - timestamp;
			var passed = checkformfields( fields );
			recordinstructtrial( "prequiz", (new Date().getTime())-timestamp, passed );
			recordFormFields();
			if ( passed ) {
				showpage("starttask");
				$(".continue").click( that.startTest );
			} else {
				showpage("redoinstruct");
				$(".continue").click( function() {
					instructobject = new Instructions();
					instructobject.start();
				});
			}
			return true;
		});
	};
	
	this.startTest = function() {
		taskStartSetup();
		testobject = new TestPhase();
	};
	
	//  First thing that happens.
	return { start: this.nextForm };
};


/********************
* CODE FOR TEST	 *
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
		});
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

			$('body').html('<h1>Testing Round Complete</h1>\
				<p>Round complete! <b>You have completed ' + (currentblock-1) +
				' out of ' + condition.maxblocks + ' total test rounds</b>.\
				You got ' + boolpercent(that.hits) + '% correct.</p>' +
				 ((boolpercent(that.hits)==100) ? '\r<p>Just one more round\
				  like that and you\'ll be done!</p>' : '\r<p>If you can get\
				  two in a row at 100% you can stop early!</p>') + 
				 '<p><strong>Remember</strong>, there is a rule that will allow\
				 you to answer correctly on every trial. It will not change:\
				 all the cards will continue to have the same label. The\
				 experiment will end as soon as you are able to answer\
				 perfectly two rounds of test items in a row.</p><p>Press\
				 "Continue" to move on to the next block.</p>\
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
	testcardsleft = cardsshown.slice(0);
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
	$("#continue").click(function () {
		finishTeardown();
		recordinstructtrial( "postquestionnaire", (new Date().getTime())-timestamp );
		submitquestionnaire();
	});
	// $('#continue').click( function(){ trainobject = new TrainingPhase(); } );
	// postback();
};

var submitquestionnaire = function() {
    recordFormFields();  // TODO Make sure this didn't break anything.
	insert_hidden_into_form(0, "subjid", subjid );
	insert_hidden_into_form(0, "data", datastring );
	$('form').submit();
};

var taskStartSetup = function () {
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
		alert( "By leaving this page, you opt out of the experiment. You are forfitting your payment. Please confirm that this is what you meant to do." );
		return "Are you sure you want to leave the experiment?";
	};
};

var finishTeardown = function () {
	window.onbeforeunload = function(){ };
};

// vi: noexpandtab tabstop=4 shiftwidth=4
