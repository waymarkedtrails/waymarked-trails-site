    
$(function () {    
    // Check if user has a modern browser
    if (Modernizr.localstorage) {
        // If first time visit or user has decided to show warning message again
        if(localStorage.getItem("dataWarning") == "1" || localStorage.getItem("dataWarning") == null ) {
            jQuery.facybox({ div: '#dataWarning' }); // Open warning message
        }
        localStorage.setItem("dataWarning", "0"); // Default do not show warning next time
    }
});
