$("#accordion .card .card-header .custom-icon-arrow-down").click(function () {
    $("#accordion .card").removeClass("is-open");
    $(this).parents(".card-header").parents(".card").addClass("is-open");
    // $(this).parents(".card-header").parents(".card").find('.custom-icon-info').show();
})
$("#accordion .card.is-open .custom-icon-arrow-down").click(function () {
    $(this).parents(".card").removeClass("is-open")
})
$(".model-item.3d-page-item button").on("click", function () {
    let displayTitle = $(this).attr("data-title");
    button = $(this);
    $(".lightbox #fileName").hide();
    $(this).parents(".custom-card").addClass("done")
    $("#modelName").html(displayTitle);
    // $(".step-2.modal-list .custom-icon-info").hide();
    let step3 = $(".step-3 .custom-icon-arrow-down");
    step3.trigger('click');
})
$(".lightbox .model-item button").on("click", function () {
    let displayTitle = $(this).attr("data-title");
    button = $(this);
    // $(".lightbox-2 .custom-icon-arrow-down").addClass("custom-icon-info text-primary").removeClass(".custom-icon-arrow-down");
    $(this).parents(".custom-card").addClass("done")
    $("#fileName").hide();
    $("#modelName").html(displayTitle);
    let step3 = $(".step-2 .custom-icon-arrow-down");
    step3.trigger('click');
})
$(".lightbox-2 .model-item button").on("click", function () {
    let displayTitle = $(this).attr("data-title");
    button = $(this);
    $(this).parents(".custom-card").addClass("done")
    $("#modelName1").html(displayTitle);
    let step3 = $(".step-3 .custom-icon-arrow-down");
    step3.trigger('click');
})