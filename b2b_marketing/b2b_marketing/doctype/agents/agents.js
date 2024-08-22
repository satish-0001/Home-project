// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Agents', {


	
	 refresh: function(frm) {
	    if(frm.doc.__onload && frm.doc.__onload.dashboard_info) {
			var info = frm.doc.__onload.dashboard_info;
			frm.dashboard.add_indicator(__('Total Leads Delivered: {0}',
				[frm.doc.success_rate]), 'blue');
		}
		frm.add_custom_button(__('Show Online Calls'), function() {
				frappe.set_route('List', 'Call', {'agents_name': frm.doc.agents_name,'status':'On-going'});
			});


	 },
	 
	 test_greeting: function(frm) {
		console.log('clicked');
			frappe.call({
				method: 'intro_greeting',
				doc: frm.doc,
			}).then(function(response) {
				console.log('--------',response.message);
				
				if (response.message){
					playAudio()
				}
				// frappe.utils.play_sound("ping")
				// frappe.msgprint(response.message);
				showSecondDialog(frm); // Show the second dialog box
			}).catch(function(err) {
				// Handle errors if any
				console.error(err);
			});

	},

	test_permission: function(frm) {
		console.log("Permission button clicked----------")
		frappe.call({
			method: 'permission',
			doc: frm.doc,
		}).then(function(response) {
			console.log('--------',response.message);
			
			if (response.message){
				playAudio()
			}
			// frappe.utils.play_sound("ping")
			// frappe.msgprint(response.message);
			showSecondDialog(frm); // Show the second dialog box
		}).catch(function(err) {
			// Handle errors if any
			console.error(err);
		});
	},


	test_problem_statement: function(frm) {
		console.log("problem_statement button clicked----------")
		frappe.call({
			method: 'problem_statement',
			doc: frm.doc,
		}).then(function(response) {
			console.log('--------',response.message);
			
			if (response.message){
				playAudio()
			}
			// frappe.utils.play_sound("ping")
			// frappe.msgprint(response.message);
			showSecondDialog(frm); // Show the second dialog box
		}).catch(function(err) {
			// Handle errors if any
			console.error(err);
		});
	},

	test_solution: function(frm) {
		console.log("solution button clicked----------")
		frappe.call({
			method: 'solution',
			doc: frm.doc,
		}).then(function(response) {
			console.log('--------',response.message);
			
			if (response.message){
				playAudio()
			}
			// frappe.utils.play_sound("ping")
			// frappe.msgprint(response.message);
			showSecondDialog(frm); // Show the second dialog box
		}).catch(function(err) {
			// Handle errors if any
			console.error(err);
		});
	},

	test_follow_up: function(frm) {
		console.log("follow_up button clicked----------")
		frappe.call({
			method: 'follow_up',
			doc: frm.doc,
		}).then(function(response) {
			console.log('--------',response.message);
			
			if (response.message){
				playAudio()
			}
			// frappe.utils.play_sound("ping")
			// frappe.msgprint(response.message);
			showSecondDialog(frm); // Show the second dialog box
		}).catch(function(err) {
			// Handle errors if any
			console.error(err);
		});
	},
	
	test_voice_option: function(frm) {
		console.log("test_voice_option button clicked----------")
		frappe.call({
			method: 'voice_test',
			doc: frm.doc,
		}).then(function(response) {
			console.log('--------',response.message);
			
			if (response.message){
				playAudio()
			}
			// frappe.utils.play_sound("ping")
			// frappe.msgprint(response.message);
			// showSecondDialog(frm); // Show the second dialog box
		}).catch(function(err) {
			// Handle errors if any
			console.error(err);
		});
	},
	

});
cur_frm.fields_dict['parent_agents'].get_query = function(doc, cdt, cdn) {
	return{
		filters: [
			['Agents', 'is_group', '=', 1],
			['Agents', 'name', '!=', doc.agents_name]
		]
	}
}


function playAudio() {
    var audio = document.createElement('audio');
	var uniqueTimestamp = new Date().getTime();
	const sitePath = frappe.urllib.get_base_url()
	audio.src = sitePath+'/files/speech.mp3?timestamp='+uniqueTimestamp;
	audio.play()
	console.log(audio)
	return audio
};

	
// function showSecondDialog(frm) {
// 	let d2 = new frappe.ui.Dialog({
// 		title: 'Enter details',
// 		fields: [
// 			{
// 				label: 'Input',
// 				fieldname: 'input',
// 				fieldtype: 'Data'
// 			},
// 		],
// 		size: 'small', 
// 		primary_action_label: 'Submit',
// 		primary_action(values) {
// 			console.log(values);
// 			frappe.call({
// 				method: 'start_chatting',
// 				doc: frm.doc,
// 				args: values,
// 				callback: function(response) {
// 					d2.set_value('input', '');
// 				}
// 			}).then(function(response) {
// 				console.log(response.message);
// 				if (response.message){
// 					playAudio()
// 				}
// 				// frappe.msgprint(response.message);
// 			}).catch(function(err) {
// 				// Handle errors if any
// 				console.error(err);
// 			});
// 		}
// 	});
	
// 	d2.show();
// }

function showSecondDialog(frm) {
    let d2 = new frappe.ui.Dialog({
        title: 'Enter details',
        fields: [
            {
                label: 'Voice Input',
                fieldname: 'voice_input',
                fieldtype: 'Data',
                // read_only: 1, 
            },
        ],
        size: 'small', 
        primary_action_label: 'Submit',
        primary_action(values) {
            console.log(values.voice_input);
            frappe.call({
                method: 'start_chatting',
                doc: frm.doc,
                args:{
					input: values.voice_input
				},
                callback: function(response) {
                    d2.set_value('voice_input', '');
                }
            }).then(function(response) {
                console.log(response.message);
                if (response.message){
                    playAudio()
                }
                // frappe.msgprint(response.message);
            }).catch(function(err) {
                console.error(err);
            });
        }
    });

    d2.fields_dict['voice_input'].$input.on('focus', function() {
        startSpeechRecognition(d2);
    });

    d2.show();
}

function startSpeechRecognition(dialog) {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    let interimTranscript = '';

    recognition.onresult = function(event) {
        interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            interimTranscript += transcript;
        }
		console.log('Speech input:', interimTranscript);
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
    };

    recognition.onend = function() {
        console.log('Speech recognition ended.');
        const currentInput = dialog.get_value('voice_input');
        dialog.set_value('voice_input', currentInput + interimTranscript);
        interimTranscript = ''; 
        if (dialog.fields_dict['voice_input'].$input.is(':focus')) {
            console.log('Restarting recognition...');
            startSpeechRecognition(dialog); 
        }
    };

    recognition.start();
}