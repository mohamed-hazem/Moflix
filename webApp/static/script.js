// Vars
let search = document.querySelector("#search");
let season = document.querySelector("#season");
let episodes = document.querySelector("#episodes");

let resultsDiv = document.querySelector("#results-div");
let loaderDiv = document.querySelector("#loader");

// On load
search.focus();

let searchSeason = "";
let searchEpisodes = "";

// Fetch Search Results
function getResults() {
    searchSeason = season.value;
    searchEpisodes = episodes.value;
    loader();

    fetch("/search?search_key="+search.value)
    .then(response => response.json())
    .then(results => showResults(results))
    .catch(e => console.log(e));
}

function showResults(results) {
    // console.log(results)
    search.value = "";
    season.value = "";
    episodes.value = "";
    search.focus();
    clearDiv(resultsDiv);
    loader(false);

    results.forEach(result => {
        addResult(result);
    });

    // Add Event Listener
    let mainDivs = document.querySelectorAll(".main");
    Array.from(mainDivs).forEach(function(element) {
        element.addEventListener('click', getCurrentResults);
    });

    // Add Event Listener for Manual Subtitle
    let subBtns = document.querySelectorAll(".subtitle");
    for (let i=0; i<subBtns.length; i++) {
        subBtns[i].addEventListener('click', (event) => {
            event.stopPropagation();
            manualSubtitle(subBtns[i].parentElement.parentElement);
        });
    }
}

// Loader
function loader(show=true) {
    let d = (show) ? "flex" : "none";
    loaderDiv.style.display = d;
}

// Add Result
function addResult(result) {
    // Main Div
    let mainDiv = document.createElement("div");
    mainDiv.setAttribute("class", "col-lg-2 col-md-6 col-sm-12 d-flex justify-content-center align-self-center main");
    mainDiv.setAttribute("data-name", result["name"]);
    mainDiv.setAttribute("data-year", result["year"]);
    mainDiv.setAttribute("data-type", result["type"]);
    mainDiv.setAttribute("data-id", result["id"]);
    
    // Item Div
    let itemDiv = document.createElement("div");
    itemDiv.setAttribute("class", "item position-relative");

    let a = document.createElement("a");

    let spanQuality = document.createElement("span");
    spanQuality.setAttribute("class", "quality");
    spanQuality.textContent = result["quality"];

    let manualSubSpan = document.createElement("i");
    manualSubSpan.setAttribute("class", "fa-regular fa-closed-captioning subtitle");

    // Img Div
    let imgDiv = document.createElement("div");
    imgDiv.setAttribute("class", "img-div position-relative");

    let img = document.createElement("img");
    img.setAttribute("class", "img-fluid")
    img.setAttribute("src", result["image"]);
    
    imgDiv.appendChild(img);

    // Detail Div
    let detailDiv = document.createElement("div");
    detailDiv.setAttribute("class", "detail ps-2");

    let title = document.createElement("h3");
    title.setAttribute("class", "title text-muted mt-1");
    title.setAttribute("title", result["name"]);
    title.textContent = result["name"];

    // Info Div
    let info = document.createElement("div");
    info.setAttribute("class", "info text-muted d-flex justify-content-between");

    let year = document.createElement("span");
    year.setAttribute("class", "year");
    year.innerHTML = '<i class="fa-regular fa-calendar"></i> '+result["year"];

    let duration = document.createElement("span");
    duration.setAttribute("class", "duration");
    if (result["duration"]) {duration.innerHTML = '<i class="fa-regular fa-clock"></i> '+result["duration"]};
    
    let type = document.createElement("span");
    type.setAttribute("class", "type");
    type.textContent = result["type"];

    info.appendChild(year);
    info.appendChild(duration);
    info.appendChild(type);

    // ------------- //
    
    detailDiv.appendChild(title);
    detailDiv.appendChild(info);
    
    // ------------- //
    
    itemDiv.appendChild(a);
    itemDiv.appendChild(spanQuality);
    if (result["type"] == "TV") itemDiv.appendChild(manualSubSpan);
    itemDiv.appendChild(imgDiv);
    itemDiv.appendChild(detailDiv);
    // ------------- //
    mainDiv.appendChild(itemDiv);
    // ------------- //
    
    resultsDiv.appendChild(mainDiv);
}

// Manual Subtitle
function manualSubtitle(parent) {
    let manualSubUrl = `/manual-subtitle?`+
    `id=${parent.getAttribute("data-id")}`+
    `&name=${parent.getAttribute("data-name")}`+
    `&season=${season.value}`;

    fetch(manualSubUrl);
}

// Help functions //
function clearDiv(div) {
    while (div.firstChild) {
        div.removeChild(div.firstChild);
    }
}

// EventListeners //

// Search Launcher
[search, season, episodes].forEach(element => {
    element.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            getResults();
        }
    })
});

// Manual Main Launcher
document.querySelector("#manual-main").addEventListener("click", () => {
    fetch('/manual-main');
})

// ============================================================== //
function getCurrentResults() {
    let dl_url = `/download?`+
    `id=${this.getAttribute("data-id")}`+
    `&type=${this.getAttribute("data-type")}`+
    `&name=${encodeURIComponent(this.getAttribute("data-name"))}`+
    `&year=${this.getAttribute("data-year")}`+
    `&season=${searchSeason}`+
    `&episodes=${searchEpisodes}`;
    fetch(dl_url);
}
// ============================================================== //