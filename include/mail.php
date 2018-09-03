<?php

require_once('PHPMailer/PHPMailerAutoload.php');

function send_mail($to, $subject, $body_plain, $body_html = null) {
    $mail = new PHPMailer;

    //$mail->SMTPDebug = 3;

    $mail->isSMTP();
    $mail->Host       = config('smtp_host');
    $mail->SMTPAuth   = true;
    $mail->Username   = config('smtp_user');
    $mail->Password   = config('smtp_password');
    $mail->SMTPSecure = config('smtp_security');
    $mail->Port       = config('smtp_port');

    $mail->CharSet = 'utf-8';

    $mail->XMailer = ' ';

    $mail->setFrom(config('smtp_from_address'),
                   config('smtp_from_name'));

    $mail->addAddress($to);

    $mail->addReplyTo(config('smtp_replyto_address'), config('smtp_replyto_name'));

    $mail->Subject = $subject;

    if ($body_html === null) {
        $mail->isHTML(false);
        $mail->Body = $body_plain;
    } else {
        $mail->isHTML(true);
        $mail->AltBody = $body_plain;
        $mail->Body    = $body_html;
    }

    //error_log('Send mail to <' . $to . '> ???');

    if (!$mail->send()) {
        error_log('Could not send mail to <' . $to . '>: ' . $mail->ErrorInfo);
        return false;
    } else {
        return true;
    }
}

function render_template($text, $vars, $is_html = false) {
    return str_replace(array_map(function($s){return "[[$s]]";}, array_keys($vars)),
                       // Perform htmlentities if necessary.
                       ($is_html ? array_map(function($s){return escape_html($s);},
                                             array_values($vars))
                                 : array_values($vars)),
                       $text);
}

function send_mail_template($to, $subject, $template_name, $template_vars) {
    $start_html =  file_get_contents("mail-templates/common-start.html");
    $end_html   =  file_get_contents("mail-templates/common-end.html");
    $body_html  = @file_get_contents("mail-templates/$template_name.html");
    $body_plain =  file_get_contents("mail-templates/$template_name.txt");

    if ($start_html === false || $end_html === false || $body_plain === false)
        fail("Could not render mail template '$template_name'");

    $body_plain = render_template($body_plain, $template_vars);

    if ($body_html === null) {
        // No HTML version available.
        send_mail($to, $subject, $body_plain);
    } else {
        $body_html = render_template($start_html . $body_html . $end_html,
                                     $template_vars, true);
        send_mail($to, $subject, $body_plain, $body_html);
    }
}
