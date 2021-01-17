function toggle_modal(id) {
  console.log(id);
  modal = new bootstrap.Modal(document.getElementById(id));
  modal.toggle();
}