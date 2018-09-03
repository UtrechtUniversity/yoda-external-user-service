<?php

// View functions.

/// htmlentities wrapper.
function escape_html($str) {
    return htmlentities($str, ENT_HTML5, 'UTF-8');
}

/// Render a named view.
/// $data is exposed to the included view and may be used to pass parameters to it.
function render_view($name, $data=array()) {
    if (!isset($data['title'])) { $data['title'] = 'Yoda external user service'; }

    require('views/common/start.phtml');
    require("views/$name.phtml");
    require('views/common/end.phtml');
}
