// static/app/scripts/editora.js

//$(document).ready(function () {
//    $('#edit-editoras').on('click', function () {
//        $('input, select').prop('disabled', false);
//        $(this).hide();
//        $('#save-editoras').show();
//    });

//    $('#save-editoras').on('click', function () {
//        $('input, select').prop('disabled', true);
//        $(this).hide();
//        $('#edit-editoras').show();
//    });
//});


$(document).ready(function () {
    $('#save-editoras').hide();
    $('#edit-editoras').on('click', function () {
        $('input[name="editoras_to_edit"]').prop('disabled', false);
        $(this).hide();
        $('#save-editoras').show();
    });

    $('#editora-form').on('submit', function (event) {
        event.preventDefault();
        var editorasToEdit = [];
        $('input[name="editoras_to_edit"]:checked').each(function () {
            editorasToEdit.push($(this).val());
        });

        // Enviar a lista de IDs selecionados para o servidor (por exemplo, via AJAX)
        // para que você possa processar a edição no Django.
        console.log('IDs das editoras a serem editadas: ', editorasToEdit);
    });
});
