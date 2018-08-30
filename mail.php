<?php

require_once('PHPMailer/PHPMailerAutoload.php');

function send_mail($to, $subject, $body) {
    $mail = new PHPMailer;

    //$mail->SMTPDebug = 3; // Enable verbose debug output

    $mail->isSMTP();
    $mail->Host       = config('smtp_host');
    $mail->SMTPAuth   = true;
    $mail->Username   = config('smtp_user');
    $mail->Password   = config('smtp_password');
    $mail->SMTPSecure = 'tls';
    $mail->Port       = config('smtp_port');

    $mail->XMailer = ' ';

    $mail->setFrom(config('smtp_from_address'),
                   config('smtp_from_name'));

    $mail->addAddress($to);

    $mail->addReplyTo(config('smtp_replyto_address'), config('smtp_replyto_name'));

    //$mail->isHTML(true);
    $mail->isHTML(false);

    $mail->Subject = $subject;
    //$mail->Body    = 'This is the HTML message body <b>in bold!</b>';
    //$mail->AltBody = $body;
    $mail->Body = $body;

    error_log('Send mail to <' . $to . '> ???');

    if (preg_match('/@v1a\.nl$/', $to)) {
        error_log('YES');
    } else {
        error_log('NO');
    }

    if(!$mail->send()) {
        error_log('Could not send mail to <' . $to . '>: ' . $mail->ErrorInfo);
        return false;
    } else {
        //echo 'Message has been sent';
        return true;
    }
}
