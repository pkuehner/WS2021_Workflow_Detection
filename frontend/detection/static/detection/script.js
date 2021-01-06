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



var modelName = document.getElementById("modelName").value;
highlightCurrentTabSelection(modelName);
