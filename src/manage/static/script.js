// TEMPUS DB SCRIPT

const gridTiles = document.querySelectorAll("#tilegrid button");

/*
const settingsModal = document.querySelector("dialog#dash-settings");
const photoLinkModal = document.querySelector("dialog#photolink");
*/

const controlModals = document.querySelectorAll("dialog.controller");

const displayBtn = document.querySelectorAll(".gallery .display-btn");
const spinnerModal = document.querySelector("dialog#spinner");

const progressForm = document.querySelector("#progress-display form");

const modalObjs = [
      {slug:"dashboard", id:"dash-settings", inputid:"timer", route:"/dashstart"},
      {slug:"photolink", id:"photo-link", inputid:"url", route:"/display-url"}

];

for (let i = 0; i < gridTiles.length; i++) {
	let tile = gridTiles[i];
	let routeUrl = tile.getAttribute("data-route");

	tile.addEventListener('click', () => {
		if (routeUrl) {
			var res = sendTileAction(routeUrl);
		} else {
      let slug = tile.getAttribute("id");
      let modalData = modalObjs.find((m) => m.slug == slug);
      let theModal = document.getElementById(modalData.id);

      theModal.showModal();
		}
	});
}

if (controlModals.length > 0) {
  controlModals.forEach((modal, i) => {
    modal.addEventListener('close', () => {
      if (modal.returnValue === "save") {
        let modalId = modal.getAttribute("id");
        let modalData = modalObjs.find((m) => m.id == modalId);

        modalDispatch(modal, "#" + modalData.inputid, modalData.route);
      }
    });
  });
}

/*
if (settingsModal) {
  settingsModal.addEventListener('close', () => {
  	if (settingsModal.returnValue === "save") {
      modalDispatch(settingsModal, "input#timer", "/dashstart");
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
*/

for (let i = 0; i < displayBtn.length; i++) {
	let disbtn = displayBtn[i];
	let routeUrl = disbtn.getAttribute("data-route");

	disbtn.addEventListener('click', () => {
		if (routeUrl) {
			var res = sendTileAction(routeUrl);
		}
	});
}

if (progressForm) {
  progressForm.addEventListener("submit", () => {
    setTimeout(() => {
      spinnerModal.showModal();

      if (spinnerModal.open == True) {
        setTimeout(() => {
          spinnerModal.close();
          alert("Year Progress display operation timed out.")
        }, 61.0 * 1000);
      }
    }, 500);
  });
}

function modalDispatch(modalEl, inputId, routeUrl) {
  let inputEl = modalEl.querySelector(inputId);
  let val = inputEl.value;

  var startRes = sendTileAction(routeUrl, { "input_data": val });
}

// showSettings();

async function sendTileAction(routeUrl, data = null) {
	try {
    setTimeout(() => { spinnerModal.showModal(); }, 500);

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
    window.location.href = "/";
	} catch (error) {
	  spinnerModal.close();
		let msg = error.message ? error.message : "Something went wrong."
		console.error(msg);
    alert(msg);
	}
}
