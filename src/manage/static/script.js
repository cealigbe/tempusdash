// TEMPUS DB SCRIPT

const gridTiles = document.querySelectorAll("#tilegrid button");
const settingsModal = document.querySelector("dialog#settings");
const photoLinkModal = document.querySelector("dialog#photolink");
const displayBtn = document.querySelectorAll(".gallery .display-btn");
const spinnerModal = document.querySelector("dialog#spinner");

for (let i = 0; i < gridTiles.length; i++) {
	let tile = gridTiles[i];
	let routeUrl = tile.getAttribute("data-route");

	tile.addEventListener('click', () => {
		if (routeUrl) {
			var res = sendTileAction(routeUrl);
		} else if (tile.getAttribute("id") == "dashboard") {
			settingsModal.showModal();
		} else if (tile.getAttribute("id") == "url-photo") {
			photoLinkModal.showModal();
		}
	});
}

if (settingsModal) {
  settingsModal.addEventListener('close', () => {
  	if (settingsModal.returnValue === "save") {
  	let timeInput = settingsModal.querySelector("input#timer");
  		let timing = timeInput.value;

  		var startRes = sendTileAction("/dashstart", {"timing": timing});
  	}
  });
}

if (photoLinkModal) {
  photoLinkModal.addEventListener('close', () => {
  	if (photoLinkModal.returnValue === "save") {
    	let urlInput = photoLinkModal.querySelector("input#url");
  		let url = urlInput.value;

  		var startRes = sendTileAction("/display-url", {"image_url": url});
  	}
  });
}

for (let i = 0; i < displayBtn.length; i++) {
	let disbtn = displayBtn[i];
	let routeUrl = disbtn.getAttribute("data-route");

	disbtn.addEventListener('click', () => {
		if (routeUrl) {
			var res = sendTileAction(routeUrl);
		}
	});
}

// showSettings();

async function sendTileAction(routeUrl, data = null) {
	try {
    setTimeout(() => {spinnerModal.showModal();}, 500)

    let tileData = new FormData();
    tileData.append("route", routeUrl)

    if (data) {
      for (const [key, val] of Object.entries(data)) {
        tileData.append(key, val);
      }
    }

		const response = await fetch(routeUrl, {
			method: 'POST',
			body: tileData
		});

		if (!response.ok) {
			throw new Error(`Response status: ${response.status}`);
		}

		const result = await response.json();
    spinnerModal.close();
		console.log(result);

		alert(result.message);
		window.location.href="/"
	} catch (error) {
	  spinnerModal.close();
		let msg = error.message ? error.message : "Something went wrong."
		console.error(msg);
    alert(msg);
	}
}



/*
async function sendSettings(data) {
	try {
		const response = await fetch("/dashstart", {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		});

		if (!response.ok) {
			throw new Error(`Response status: ${response.status}`);
		}

		const result = await response.json();
		console.log(result);

		alert(result.message);
	} catch (error) {
		console.error(error.message);
	}
}
*/
