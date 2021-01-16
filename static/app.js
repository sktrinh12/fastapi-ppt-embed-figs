function performPPTAUTO() {
	var files = document.getElementById("required_files").files
	var input_subtext = $("#input-text-subtext");
	var input_platenbr = $("#input-text-platenum");
	var formData = new FormData();
	var endpoint = '/generate_ppt';
	var countTypes = 0;

	if (files.length < 3 || files.length > 3) {
		swal({
			title: "Error",
			text: "Insufficient number of files, must provide 3",
			icon: "error",
			buttons: true
		});
	} else if (!input_platenbr || !input_subtext) {
		swal({
			title: "Error",
			text: "Must enter subtext and plate number",
			icon: "error",
			buttons: true
		});

	} else {

		formData.append('platenum', input_platenbr.val());
		formData.append('subtext', input_subtext.val());
		// console.log(data);
		// for (var pair of formData.entries()) {
		// 	console.log(pair[0] + ', ' + pair[1]);
		// }

		for (var i = 0; i < files.length; i++) {
			if (isImage(files[i].name.toString())) {
				countTypes ++;
			};
			if (isCSV(files[i].name.toString())) {
				countTypes ++;
			};
			formData.append('thefiles', files[i])
			console.log(files[i]);
		}


	if (countTypes !== 3) {
		swal({
			title: "Error",
			text: "The file-types seem wrong, ensure there are two '.png' files and one '.csv' file",
			icon: "error",
			buttons: true
		});
		console.log(`countTypes: ${countTypes}`);
	} else {

	$body = $("body");

	// nested ajax
	$.ajax({
			url: '/purge'
			})
			.done( function() {
				console.log('purged current directory');
			})
			.fail( function( reason ) {
				console.info( reason );
			})
			.then( function(data) {

				$.ajax( {
					type: 'POST',
					url: endpoint,
					data: formData,
					contentType: false,
					cache: false,
					processData: false,
					beforeSend: function() {
						// show loading animation
						$body.addClass("loading");
					},
					success: function(data) {
						swal({
							title: "Files submitted",
							text: "Finished processing the ppt file",
							icon: "success",
							buttons: true
						});
						$("#download-btn").show();
					},
					complete: function(data) {
						// hide loading animation
						$body.removeClass("loading");
					},
					error: function(err) {
						console.log(err);
					}
				});
			})
	}
}
}

function getExtension(filename) {
	var parts = filename.split(".");
	return parts[parts.length - 1];
}


function isImage(filename) {
	var ext = getExtension(filename);
	switch (ext.toLowerCase()) {
		case 'png':
			return true;
	}
	return false;
}

function isCSV(filename) {
	var ext = getExtension(filename);
	switch (ext.toLowerCase()) {
		case 'csv':
			return true;
	}
	return false;
}
