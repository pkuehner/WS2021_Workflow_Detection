document.querySelector("#file-upload").onchange = function(){
    document.querySelector("#file-name").textContent = this.files[0].name;
}

function uploadFile(){
    document.getElementById("spinner").style.display = 'block';
    document.getElementById("imagemodel").style.display = 'none';
}

function highlightCurrentTabSelection(id) {
    var element = document.getElementById(id);
    element.classList.add("selected");
}

// just grab a DOM element
var element = document.querySelector('#imagemodel')

// And pass it to panzoom
panzoom(element, {
    bounds: true,
    boundsPadding: 0.1
});

var modelName = document.getElementById("modelName").value;
highlightCurrentTabSelection(modelName);


function exportJson(el) {
    var patterns = document.getElementById("patternsJson").value;
    console.log(patterns)
    var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(patterns));
    el.setAttribute("href", "data:" + data);
    el.setAttribute("download", "data.json");
}
