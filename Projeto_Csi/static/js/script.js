
function toggleWidth() {
    var centralEsquerda = document.getElementById('central_esquerda');
    var centralEsquerdaConteudoP = document.getElementsByClassName('central_esquerda_conteudo_p');
    var centralEsquerdaConteudo = document.getElementById('central_esquerda_conteudo');

    if (centralEsquerda.style.width === '0px') {
        centralEsquerda.style.width = '300px';

        for (var i = 0; i < centralEsquerdaConteudoP.length; i++) {
            centralEsquerdaConteudoP[i].style.display = 'block';
        }

        centralEsquerdaConteudo.style.margin = '50px 35px;';
        centralEsquerdaConteudo.style.transition = 'margin 0.5s ease-in-out';
    } else {
        for (var i = 0; i < centralEsquerdaConteudoP.length; i++) {
            centralEsquerdaConteudoP[i].style.display = 'none';
        }

        centralEsquerda.style.width = '0px';
        centralEsquerdaConteudo.style.margin = '50px 35px;';
        centralEsquerdaConteudo.style.transition = 'margin 0.5s ease-in-out';
    }
}
/////////////



function fechar_chat() {
    var centralEsquerda = document.getElementById('chat_background');
    if (centralEsquerda.style.display === 'block') {
        centralEsquerda.style.display = 'none';
    } else {
        centralEsquerda.style.display = 'block';
    }
}


/////////////////


function toggleSubMenu(id, arrowId) {
    var submenu = document.getElementById(id);
    var arrow = document.getElementById(arrowId);   

    if (submenu.style.display === "none") {
        submenu.style.display = "block";
        arrow.classList.add('collapsed');
        arrow.style.transform = "rotate(180deg)";
    } else {
        submenu.style.display = "none";
        arrow.classList.remove('collapsed');
        arrow.style.transform = "rotate(270deg)";
    }
}