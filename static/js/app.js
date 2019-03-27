// $(".line-container").click(function() {
//   $(".line-container")
//     .not(this)
//     .each(function() {
//       $(this).toggleClass("not-active active");
//     })
//     .parent()
//     .find(".status-container")
//     .addClass("not-active");
//   $(this).toggleClass("active");
//   $(".line-container")
//     .parent()
//     .toggleClass("spread-list");
//   $(".status-container").toggleClass("not-active");
// });
$(".line").popover({
  trigger: "focus"
});
