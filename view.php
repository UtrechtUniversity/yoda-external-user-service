<?php

function escape_html($str) {
    return htmlentities($str, ENT_HTML5, 'UTF-8');
}

function render_view($name, $data=array()) {
    if (!isset($data['title'])) { $data['title'] = 'Yoda external user service'; }

    #var_dump($data);

    include('views/common/start.phtml');
    include("views/$name.phtml");
    include('views/common/end.phtml');
}
