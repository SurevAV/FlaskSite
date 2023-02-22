function reply_click(clicked_id) {
    var input = document.getElementById('to');
    if (!input.value.includes(clicked_id)) {
        input.value = input.value + clicked_id + ',';
    }
}

function hide_block() {
    var x = document.getElementById("block-menu");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}