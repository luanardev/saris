$(document).ready(function () {

    $("input[name=selectall]").click(function () {
        $("input[name=selection]").prop("checked", this.checked);
    });

    $("input[name=selection]").click(function () {
        if (!$(this).prop("checked")) {
            $("input[name=selectall]").prop("checked", false);
        }
    });

    $("button[name=delete]").click(function (e) {
        e.preventDefault();

        var form = $("form[name=deleteForm]")
        var formAction = form.attr("action")
        var formMethod = form.attr("method")
        var formArray = form.serializeArray()
        
        var selected = [];

        $("input[name=selection]").each(function () {
            if ($(this).is(":checked")) {
                selected.push($(this).val());
            }
        });

        if (selected.length <= 0) {
            return false;
        }

        const confirmed = confirm("Are you sure you want to delete?");
        if (confirmed == false) {
            return false;
        }
        
        formArray.push({ name: "selection", value: selected });
        var formData = $.param(formArray);

        $.ajax({
            type: formMethod,
            url: formAction,
            data: formData,
            success: function (response) {
                alert(response.message);
                location.reload()
            },
            error: function (response) {
                alert(response.responseJSON.error);
            }
        });
    });
    
});