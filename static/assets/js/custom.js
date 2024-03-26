$(document).ready(function () {
    $("select").select2({
        width: "resolve",
        theme: "classic",
        allowClear: true,
    });

    $("body").on("shown.bs.modal", ".modal", function () {
        $(this).find("select").each(function () {
            $(this).select2({
                dropdownParent: $('.modal'),
                width: "resolve",
                theme: "classic",
            });
        });
    });
});
