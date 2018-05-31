
function toggleForm(event) {
  if (event !== undefined) {
    event.preventDefault()
  }
  $('#taskCreateForm').toggle()
}

function toggleRepeat(event) {
  $('.taskRepeat').toggle()
}
