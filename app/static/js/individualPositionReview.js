let edit_sections = document.querySelectorAll(".editor")

  for(i=0; i < edit_sections.length; i++){
    const quill = new Quill(document.getElementById(edit_sections[i].id), {
        theme: 'snow'
    });
  }
