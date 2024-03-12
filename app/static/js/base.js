function msgFlash(flash_message, status){
    var category = (status === "success") ? "success" : ((status === "fail") ? "danger" : "warning");
    $("#flash_container").prepend('<div class="alert alert-'+ category +'" role="alert" id="flasher">'+flash_message+'</div>');
    $("#flasher").delay(5000).fadeOut();
}
