// main elements
let search = document.querySelector("#search");
let season = document.querySelector("#season");
let episodes = document.querySelector("#episodes");

let resultsDiv = document.querySelector("#results-div");
let loaderDiv = document.querySelector("#loader");

// on load
search.focus();

let searchSeason = "";
let searchEpisodes = "";

// fetch search results
function getResults() {
    searchSeason = season.value;
    searchEpisodes = episodes.value;
    loader();

    fetch("/search?search_key="+search.value)
    .then(response => response.json())
    .then(results => showResults(results))
    .catch(e => console.log(e));
}

// show results
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

    // add event listener to download a result 
    let mainDivs = document.querySelectorAll(".main");
    Array.from(mainDivs).forEach(function(element) {
        element.addEventListener("click", downloadResult);
    });

    // add event listener to download a result subtitle manually
    let subBtns = document.querySelectorAll(".subtitles");
    for (let i=0; i<subBtns.length; i++) {
        subBtns[i].addEventListener("click", (event) => {
            event.stopPropagation();
            downloadSubtitle(subBtns[i].closest("div.main"));
        });
    }
}

// loader
function loader(show=true) {
    let d = (show) ? "flex" : "none";
    loaderDiv.style.display = d;
}

// add a result
function addResult(result) {
    // main div
    let mainDiv = document.createElement("div");
    mainDiv.setAttribute("class", "col-lg-2 col-md-6 col-sm-12 d-flex justify-content-center align-self-center main");
    mainDiv.setAttribute("data-name", result["name"]);
    mainDiv.setAttribute("data-year", result["year"]);
    mainDiv.setAttribute("data-type", result["type"]);
    mainDiv.setAttribute("data-url", result["url"]);
    
    // item div
    let itemDiv = document.createElement("div");
    itemDiv.setAttribute("class", "item position-relative");

    let a = document.createElement("a");

    // image div
    let imgDiv = document.createElement("div");
    imgDiv.setAttribute("class", "img-div position-relative");

    let img = document.createElement("img");
    img.setAttribute("class", "img-fluid")
    img.setAttribute("src", result["image"]);
    
    imgDiv.appendChild(img);

    // detail div
    let detailDiv = document.createElement("div");
    detailDiv.setAttribute("class", "detail ps-2");

    let title = document.createElement("h3");
    title.setAttribute("class", "title text-muted mt-1");
    title.setAttribute("title", result["name"]);
    title.textContent = result["name"];

    // info div
    let info = document.createElement("div");
    info.setAttribute("class", "info text-muted d-flex justify-content-between");

    let year = document.createElement("span");
    year.setAttribute("class", "year");
    year.innerHTML = '<i class="fa-regular fa-calendar"></i> '+result["year"];

    let duration = document.createElement("span");
    duration.setAttribute("class", "duration");
    if (result["duration"]) {duration.innerHTML = '<i class="fa-regular fa-clock"></i> '+result["duration"]};
    
    let subtitles = document.createElement("span");
    subtitles.innerHTML = '<i class="fa-regular fa-closed-captioning subtitles"></i>';

    info.appendChild(year);
    info.appendChild(duration);
    info.appendChild(subtitles);

    // ------------- //
    
    detailDiv.appendChild(title);
    detailDiv.appendChild(info);
    
    // ------------- //
    
    itemDiv.appendChild(a);
    itemDiv.appendChild(imgDiv);
    itemDiv.appendChild(detailDiv);
    // ------------- //
    mainDiv.appendChild(itemDiv);
    // ------------- //
    
    resultsDiv.appendChild(mainDiv);
}

// download subtitle
function downloadSubtitle(parent) {
    let dlSubUrl = `/download-subtitle?`+
    `vtype=${parent.getAttribute("data-type")}`+
    `&url=${parent.getAttribute("data-url")}`+
    `&name=${parent.getAttribute("data-name")}`+
    `&year=${parent.getAttribute("data-year")}`+
    `&season=${season.value}`;

    fetch(dlSubUrl);
}

// -- Helpers -- //
function clearDiv(div) {
    while (div.firstChild) {
        div.removeChild(div.firstChild);
    }
}

// -- EventListeners -- //

// search inputs
[search, season, episodes].forEach(element => {
    element.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            getResults();
        }
    })
});

// open staged button
document.querySelector("#open-staged").addEventListener("click", () => {
    fetch('/open-staged');
})

// ============================================================== //

// download
function downloadResult() {
    let dl_url = `/download?`+
    `url=${this.getAttribute("data-url")}`+
    `&vtype=${this.getAttribute("data-type")}`+
    `&name=${encodeURIComponent(this.getAttribute("data-name"))}`+
    `&year=${this.getAttribute("data-year")}`+
    `&season=${searchSeason}`+
    `&episodes=${searchEpisodes}`;
    fetch(dl_url);
}
// ============================================================== //