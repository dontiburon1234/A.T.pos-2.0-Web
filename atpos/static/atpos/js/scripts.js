function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
  function cambiarEstado(id, tipo) {
    // Realizar la petición AJAX al servidor para cambiar el estado
    fetch(`/cambiar_estado/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Obtener el token CSRF de las cookies
        },
        body: JSON.stringify({ id: id, tipo: tipo }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.estado === 'activo') {
            document.getElementById('boton_estado_'+id).innerHTML = 'Activo';
            document.getElementById('boton_estado_'+id).className = 'btn btn-success';
        } else if (data.estado === 'inactivo') {
            document.getElementById('boton_estado_'+id).innerHTML = 'Inactivo';
            document.getElementById('boton_estado_'+id).className = 'btn btn-danger';
        }
    })
    .catch(error => console.error('Error:111', error));
  }
  
  
  
  
  