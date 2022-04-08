

$(function () {
  $('[data-toggle="popover"]').popover()
})

$('.slider').on('input', function() {
	let val = $(this).val();
  let max_value = $(this).prop("max");

  $("#" + this.id + "_value").html(val);
  help_text = "";
  help_class = "";
  help_category = this.id;
  if (help_category == "jobSpecific") {
    help_category = "job specific"
  }
  if (val < max_value*10/20) {
    help_text = "The student has failed to met your "+help_category+" expectations. Please leave a comment about why and how."
    help_class = "alert-danger";
  } else if (val < max_value*14/20) {
    help_text = "The student has not fully met your "+help_category+" expectations."
    help_class = "alert-warning";
  } else if (val > max_value*16/20) {
    help_text = "The student has exceeded your "+help_category+" expectations. Please leave a comment about why and how."
    help_class = "alert-success";
  } else if (val >= max_value*14/20) {
    help_text = "The student has met your "+help_category+" expectations."
    help_class = "alert-info";
  }

  $("#" + this.id + "_help").html(help_text);
  $("#" + this.id + "_help").removeClass("alert-success").removeClass("alert-danger").removeClass("alert-warning").removeClass("alert-info");
  $("#" + this.id + "_help").addClass(help_class);
  $("#" + this.id + "_help").removeAttr("hidden");

  update_sum();
});

function update_sum() {
  sum = 0;
  $(".values").each(function() {
      sum += parseFloat($(this).text());
    })
  $("#total_value").html(sum);

  if (sum < 60) {
    message = "Not meeting expectations of the department"
  } else if (sum < 70) {
    message = "Needs improvement"
  } else if (sum < 80) {
    message = "Meets expectations"
  } else if (sum < 90) {
    message = "Exceeds expectations"
  } else {
    message = "Exceptional labor performance"
  }
  $("#score_text").html(message);
  }

$("#finalSubmitButton").click(function() {
  $("#isSubmitted").val("True");
	console.log($("#isSubmitted").val())
});

$('#submit_as_final').change(function() {
  if (this.checked) {
    $("#transcriptComments").attr("disabled", false);
  } else {
    $("#transcriptComments").attr("disabled", true);
    $("#transcriptComments").val(null);
  }
})
