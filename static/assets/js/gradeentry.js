$(document).ready(function () {
    new DataTable(".table");
});

$(document).on("focusout", ".editable-ca", function () {
    var student_course = $(this).attr("data-id");
    var endsemester_grade = $(this).attr("data-eos");
    var continous_grade = $(this).text();
    submit_grade(student_course, continous_grade, endsemester_grade);
});

$(document).on("focusout", ".editable-eos", function () {
    var student_course = $(this).attr("data-id");
    var continous_grade = $(this).attr("data-ca");
    var endsemester_grade = $(this).text();
    submit_grade(student_course, continous_grade, endsemester_grade);
});

function submit_grade(student_course, continous_grade, endsemester_grade) {
    var form = $("#gradeform");
    var formAction = form.attr("action");
    var formMethod = form.attr("method");
    var formData = form.serializeArray();

    formData.push(
        { name: "student_course", value: student_course },
        { name: "continous_grade", value: continous_grade },
        { name: "endsemester_grade", value: endsemester_grade }
    );

    var serverData = $.param(formData);

    $.ajax({
        type: formMethod,
        url: formAction,
        data: serverData,
        success: function (response) {
            console.log(response.message)
        },
        error: function (response) {
            alert(response.responseJSON.error)
        },
    });
}
