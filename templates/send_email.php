<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Collect form data
    $company_name = $_POST['company_name'];
    $customer_name = $_POST['customer_name'];
    $customer_email = $_POST['customer_email'];
    $customer_phone = $_POST['customer_phone'];
    $customer_street = $_POST['customer_street'];
    $customer_zipcode = $_POST['customer_zipcode'];
    $customer_city = $_POST['customer_city'];

    // Email configuration
    $to = "info@lightvertise.de"; // Replace with your email address
    $subject = "Neue Anfrage von " . $customer_name;
    $headers = "From: " . $customer_email . "\r\n";
    $headers .= "Reply-To: " . $customer_email . "\r\n";
    $headers .= "Content-Type: text/html; charset=UTF-8\r\n";

    // Email content
    $message = "<html><body>";
    $message .= "<h2>Neue Anfrage</h2>";
    $message .= "<p><strong>Firma:</strong> " . $company_name . "</p>";
    $message .= "<p><strong>Name:</strong> " . $customer_name . "</p>";
    $message .= "<p><strong>E-mail:</strong> " . $customer_email . "</p>";
    $message .= "<p><strong>Telefon:</strong> " . $customer_phone . "</p>";
    $message .= "<p><strong>Straße:</strong> " . $customer_street . "</p>";
    $message .= "<p><strong>PLZ:</strong> " . $customer_zipcode . "</p>";
    $message .= "<p><strong>Stadt:</strong> " . $customer_city . "</p>";
    $message .= "</body></html>";

    // Send email
    if (mail($to, $subject, $message, $headers)) {
        echo "Email sent successfully!";
    } else {
        echo "Failed to send email.";
    }
}
?>
