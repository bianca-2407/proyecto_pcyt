// Simple interactivity: search focus and sample button handlers
document.addEventListener('DOMContentLoaded',()=>{
  const search=document.querySelector('.search')
  if(search){
    search.addEventListener('keydown',e=>{
      if(e.key==='Enter'){
        alert('Buscar: '+search.value)
      }
    })
  }

  document.querySelectorAll('.btn-small, .btn-primary').forEach(btn=>{
    btn.addEventListener('click',()=>{
      alert('Función demo: botón pulsado')
    })
  })
})
